from datetime import datetime, timedelta
from fastapi import Query, APIRouter, Path, HTTPException, status, Depends, Header
from typing import Optional, List, Dict
from pydantic import BaseModel
from enum import Enum
from app.db import execute_query, connect_db, close_db
from app.utils.auth_util import get_current_user, require_roles
import httpx
import uuid

router = APIRouter(prefix="/reservations")

RESERVATION_EXPIRY_MINUTES = 10
ZARINPAL_MERCHANT_ID = "XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX"
ZARINPAL_API = "https://sandbox.zarinpal.com/pg/v4/payment/request.json"
ZARINPAL_VERIFY_API = "https://sandbox.zarinpal.com/pg/v4/payment/verify.json"
CALLBACK_URL = "https://dwin.codes/payments/verify"

class ReservationStatus(str, Enum):
    TEMPORARY = "temporary"
    RESERVED = "reserved"
    PAID = "paid"
    CANCELED = "canceled"
    EXPIRED = "expired"

class TransportType(str, Enum):
    PLANE = "plane"
    TRAIN = "train"
    BUS = "bus"

class ReservationCreate(BaseModel):
    ticket_id: int
    notes: Optional[str] = None

class ReservationUpdate(BaseModel):
    status: Optional[ReservationStatus] = None
    notes: Optional[str] = None

class ReservationResponse(BaseModel):
    id: int
    user_id: int
    ticket_id: int
    status: ReservationStatus
    price_paid: Optional[float] = None
    currency: Optional[str] = None
    reserved_at: datetime
    expires_at: Optional[datetime] = None
    payment_id: Optional[int] = None
    notes: Optional[str] = None
    ticket_details: Optional[dict] = None
    payment_details: Optional[dict] = None

class PaymentRequest(BaseModel):
    payment_method_id: int
    amount: float
    currency: str = "IRR"

class ReservationStatsResponse(BaseModel):
    total_reservations: int
    temporary: int
    reserved: int
    paid: int
    canceled: int
    by_transport_type: Dict[str, int]

async def get_reservation_details(reservation_id: int) -> Optional[dict]:
    await connect_db()
    reservation = await execute_query(
        """
        SELECT r.*, 
               t.departure_city, t.arrival_city, t.departure_time, 
               t.arrival_time, t.price as ticket_price, t.currency as ticket_currency,
               t.transport_type, t.class_type, t.available_seats,
               p.status as payment_status, p.transaction_id, p.payment_date
        FROM user_reservations r
        JOIN travel_tickets t ON r.ticket_id = t.id
        LEFT JOIN payments p ON r.payment_id = p.id
        WHERE r.id = %s
        """,
        (reservation_id,),
        fetch_one=True
    )
    
    if reservation:
        reservation["ticket_details"] = {
            "departure_city": reservation.pop("departure_city"),
            "arrival_city": reservation.pop("arrival_city"),
            "departure_time": reservation.pop("departure_time"),
            "arrival_time": reservation.pop("arrival_time"),
            "price": reservation.pop("ticket_price"),
            "currency": reservation.pop("ticket_currency"),
            "transport_type": reservation.pop("transport_type"),
            "class_type": reservation.pop("class_type"),
            "available_seats": reservation.pop("available_seats")
        }
        
        if reservation["payment_id"]:
            reservation["payment_details"] = {
                "status": reservation.pop("payment_status"),
                "transaction_id": reservation.pop("transaction_id"),
                "payment_date": reservation.pop("payment_date")
            }
    
    await close_db()
    return reservation

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=ReservationResponse)
async def create_reservation(
    reservation: ReservationCreate,
    current_user: dict = Depends(get_current_user)
):
    await connect_db()

    ticket = await execute_query(
        """
        SELECT * FROM travel_tickets 
        WHERE id = %s AND status = 'available' AND available_seats > 0
        """,
        (reservation.ticket_id,),
        fetch_one=True
    )
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not available or sold out"
        )

    active_reservation = await execute_query(
        """
        SELECT 1 FROM user_reservations 
        WHERE ticket_id = %s AND user_id = %s AND status IN ('temporary', 'reserved')
        """,
        (reservation.ticket_id, current_user["user_id"]),
        fetch_one=True
    )
    if active_reservation:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You already have an active reservation for this ticket"
        )

    reserved_at = datetime.utcnow()
    expires_at = reserved_at + timedelta(minutes=RESERVATION_EXPIRY_MINUTES)
    
    reservation_id = await execute_query(
        """
        INSERT INTO user_reservations (
            user_id, ticket_id, status, 
            reserved_at, expires_at, notes
        ) VALUES (%s, %s, 'temporary', %s, %s, %s)
        RETURNING id
        """,
        (
            current_user["user_id"],
            reservation.ticket_id,
            reserved_at,
            expires_at,
            reservation.notes
        ),
        fetch_one=True
    )

    await execute_query(
        "UPDATE travel_tickets SET available_seats = available_seats - 1 WHERE id = %s",
        (reservation.ticket_id,),
        commit=True
    )
    await close_db()
    return await get_reservation_details(reservation_id["id"])

@router.get("/{reservation_id}", response_model=ReservationResponse)
async def get_reservation(
    reservation_id: int,
    current_user: dict = Depends(get_current_user)
):
    reservation = await get_reservation_details(reservation_id)
    await connect_db()

    if not reservation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reservation not found"
        )
    
    if (reservation["user_id"] != current_user["user_id"] and 
        not await has_permission(current_user["user_id"], "view_all:reservations")):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this reservation"
        )
    
    await close_db()
    return reservation

@router.head("/{reservation_id}")
async def check_reservation_exists(
    reservation_id: int,
    current_user: dict = Depends(get_current_user)
):
    await connect_db()
    reservation = await execute_query(
        "SELECT 1 FROM user_reservations WHERE id = %s",
        (reservation_id,),
        fetch_one=True
    )
    
    if not reservation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reservation not found"
        )
    
    if not await has_permission(current_user["user_id"], "view_all:reservations"):
        user_reservation = await execute_query(
            "SELECT 1 FROM user_reservations WHERE id = %s AND user_id = %s",
            (reservation_id, current_user["user_id"]),
            fetch_one=True
        )
        if not user_reservation:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to access this reservation"
            )
    await close_db()
    return {}

@router.put("/{reservation_id}", response_model=ReservationResponse)
async def update_reservation(
    reservation_id: int,
    update: ReservationUpdate,
    current_user: dict = Depends(get_current_user)
):
    await connect_db()
    reservation = await execute_query(
        "SELECT * FROM user_reservations WHERE id = %s",
        (reservation_id,),
        fetch_one=True
    )
    if not reservation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reservation not found"
        )
    
    if (reservation["user_id"] != current_user["user_id"] and 
        not await has_permission(current_user["user_id"], "manage_all:reservations")):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this reservation"
        )
    
    set_clause = []
    params = []
    
    if update.status:
        valid_transitions = {
            "temporary": ["reserved", "canceled"],
            "reserved": ["paid", "canceled"],
            "paid": ["canceled"],
            "canceled": [],
            "expired": []
        }
        
        current_status = reservation["status"]
        if update.status.value not in valid_transitions.get(current_status, []):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot change status from {current_status} to {update.status.value}"
            )
        
        set_clause.append("status = %s")
        params.append(update.status.value)
        
        if update.status.value == "canceled":
            await execute_query(
                "UPDATE travel_tickets SET available_seats = available_seats + 1 WHERE id = %s",
                (reservation["ticket_id"],),
                commit=True
            )
    
    if update.notes is not None:
        set_clause.append("notes = %s")
        params.append(update.notes)
    
    if not set_clause:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields to update"
        )
    
    params.append(reservation_id)
    
    try:
        await execute_query(
            f"UPDATE user_reservations SET {', '.join(set_clause)} WHERE id = %s",
            params,
            commit=True
        )
        await close_db()
        return await get_reservation_details(reservation_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )