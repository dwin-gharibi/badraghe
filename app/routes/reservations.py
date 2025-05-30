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

@router.delete("/{reservation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_reservation(
    reservation_id: int,
    current_user: dict = Depends(get_current_user)
):
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
        not await has_permission(current_user["user_id"], "delete_all:reservations")):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this reservation"
        )
    
    if reservation["status"] in ["temporary", "reserved"]:
        await execute_query(
            "UPDATE travel_tickets SET available_seats = available_seats + 1 WHERE id = %s",
            (reservation["ticket_id"],),
            commit=True
        )
    
    await execute_query(
        "DELETE FROM user_reservations WHERE id = %s",
        (reservation_id,),
        commit=True
    )

@router.post("/{reservation_id}/pay", status_code=status.HTTP_200_OK)
async def pay_for_reservation(
    reservation_id: int,
    payment: PaymentRequest,
    current_user: dict = Depends(get_current_user)
):
    await connect_db()

    reservation = await execute_query(
        """
        SELECT r.*, t.price, t.currency
        FROM user_reservations r
        JOIN travel_tickets t ON r.ticket_id = t.id
        WHERE r.id = %s AND r.user_id = %s AND r.status IN ('temporary', 'reserved')
        """,
        (reservation_id, current_user["user_id"]),
        fetch_one=True
    )
    if not reservation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reservation not found or not payable"
        )
    
    if abs(float(reservation["price"]) - payment.amount) > 0.01:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Payment amount must be {reservation['price']} {reservation['currency']}"
        )
    
    payment_method = await execute_query(
        "SELECT 1 FROM payment_methods WHERE id = %s AND is_active = TRUE",
        (payment.payment_method_id,),
        fetch_one=True
    )
    if not payment_method:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid payment method"
        )
    
    transaction_id = f"txn_{uuid.uuid4().hex[:16]}"
    description = f"Payment for reservation {reservation_id}"
    
    if payment.currency == "IRR":
        payload = {
            "merchant_id": ZARINPAL_MERCHANT_ID,
            "amount": int(payment.amount),
            "callback_url": f"{CALLBACK_URL}?reservation_id={reservation_id}&user_id={current_user['user_id']}",
            "description": description,
            "metadata": {
                "reservation_id": reservation_id,
                "user_id": current_user["user_id"]
            }
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(ZARINPAL_API, json=payload)
            result = response.json()
        
        if result.get("data") and result["data"].get("code") == 100:
            authority = result["data"]["authority"]
            payment_url = f"https://sandbox.zarinpal.com/pg/StartPay/{authority}"
            
            payment_id = await execute_query(
                """
                INSERT INTO payments (
                    user_id, reservation_id, amount,
                    payment_method_id, status, transaction_id,
                    currency, payment_details
                ) VALUES (%s, %s, %s, %s, 'pending', %s, %s, %s)
                RETURNING id
                """,
                (
                    current_user["user_id"],
                    reservation_id,
                    payment.amount,
                    payment.payment_method_id,
                    authority,
                    payment.currency,
                    {"payment_url": payment_url, "gateway": "zarinpal"}
                ),
                fetch_one=True
            )
            
            return {
                "payment_url": payment_url,
                "payment_id": payment_id["id"],
                "status": "pending"
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Payment gateway error"
            )
    else:
        payment_id = await execute_query(
            """
            INSERT INTO payments (
                user_id, reservation_id, amount,
                payment_method_id, status, transaction_id, currency
            ) VALUES (%s, %s, %s, %s, 'successful', %s, %s)
            RETURNING id
            """,
            (
                current_user["user_id"],
                reservation_id,
                payment.amount,
                payment.payment_method_id,
                transaction_id,
                payment.currency
            ),
            fetch_one=True
        )
        
        await execute_query(
            """
            UPDATE user_reservations 
            SET status = 'paid', payment_id = %s 
            WHERE id = %s
            """,
            (payment_id["id"], reservation_id),
            commit=True
        )
        
        return {
            "payment_id": payment_id["id"],
            "status": "successful",
            "transaction_id": transaction_id
        }

@router.get("/{reservation_id}/verify-payment", response_model=dict)
async def verify_payment(
    reservation_id: int,
    Authority: str = Query(..., alias="Authority"),
    Status: str = Query(..., alias="Status"),
    current_user: dict = Depends(get_current_user)
):
    if Status != "OK":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Payment was canceled or failed"
        )

    payment = await execute_query(
        """
        SELECT p.*, r.user_id
        FROM payments p
        JOIN user_reservations r ON p.reservation_id = r.id
        WHERE p.transaction_id = %s AND p.status = 'pending' AND r.id = %s
        """,
        (Authority, reservation_id),
        fetch_one=True
    )
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pending payment not found"
        )
    
    if payment["user_id"] != current_user["user_id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to verify this payment"
        )

    verify_payload = {
        "merchant_id": ZARINPAL_MERCHANT_ID,
        "amount": int(payment["amount"]),
        "authority": Authority,
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(ZARINPAL_VERIFY_API, json=verify_payload)
        result = response.json()

    if result.get("data") and result["data"].get("code") == 100:
        await execute_query(
            """
            UPDATE payments 
            SET status = 'successful', 
                payment_date = NOW(),
                updated_at = NOW(),
                payment_details = %s
            WHERE id = %s
            """,
            (result["data"], payment["id"]),
            commit=True
        )
        
        await execute_query(
            """
            UPDATE user_reservations 
            SET status = 'paid', 
                payment_id = %s, 
                updated_at = NOW() 
            WHERE id = %s
            """,
            (payment["id"], reservation_id),
            commit=True
        )
        
        return {"status": "successful", "message": "Payment verified successfully"}
    else:
        await execute_query(
            """
            UPDATE payments 
            SET status = 'failed', 
                updated_at = NOW(),
                payment_details = %s
            WHERE id = %s
            """,
            (result.get("errors", {}), payment["id"]),
            commit=True
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Payment verification failed"
        )

@router.post("/cleanup-expired", status_code=status.HTTP_200_OK)
async def cleanup_expired_reservations(
    current_user: dict = Depends(require_roles("admin"))
):
    expired_reservations = await execute_query(
        """
        SELECT id, ticket_id FROM user_reservations
        WHERE status = 'temporary' AND expires_at <= NOW()
        """,
        fetch_all=True
    )

    for res in expired_reservations:
        await execute_query(
            "UPDATE user_reservations SET status = 'expired' WHERE id = %s",
            (res["id"],),
            commit=True
        )
        
        await execute_query(
            "UPDATE travel_tickets SET available_seats = available_seats + 1 WHERE id = %s",
            (res["ticket_id"],),
            commit=True
        )

    return {"canceled_reservations_count": len(expired_reservations)}

@router.get("/user/{user_id}/history", response_model=List[ReservationResponse])
async def get_user_reservation_history(
    user_id: int,
    status: Optional[ReservationStatus] = None,
    transport_type: Optional[TransportType] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    skip: int = 0,
    limit: int = 100,
    current_user: dict = Depends(get_current_user)
):
    if user_id != current_user["user_id"] and not await has_permission(current_user["user_id"], "view_all:reservations"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this user's reservations"
        )
    
    query = """
    SELECT r.*, 
           t.departure_city, t.arrival_city, t.departure_time, 
           t.arrival_time, t.price as ticket_price, t.currency as ticket_currency,
           t.transport_type, t.class_type, t.available_seats,
           p.status as payment_status, p.transaction_id, p.payment_date
    FROM user_reservations r
    JOIN travel_tickets t ON r.ticket_id = t.id
    LEFT JOIN payments p ON r.payment_id = p.id
    WHERE r.user_id = %s
    """
    params = [user_id]
    
    if status:
        query += " AND r.status = %s"
        params.append(status.value)
    
    if transport_type:
        query += " AND t.transport_type = %s"
        params.append(transport_type.value)
    
    if start_date:
        query += " AND r.reserved_at >= %s"
        params.append(start_date)
    
    if end_date:
        query += " AND r.reserved_at <= %s"
        params.append(end_date)
    
    query += " ORDER BY r.reserved_at DESC LIMIT %s OFFSET %s"
    params.extend([limit, skip])
    
    reservations = await execute_query(query, params, fetch_all=True)
    
    formatted_reservations = []
    for res in reservations:
        formatted = {
            **res,
            "ticket_details": {
                "departure_city": res.pop("departure_city"),
                "arrival_city": res.pop("arrival_city"),
                "departure_time": res.pop("departure_time"),
                "arrival_time": res.pop("arrival_time"),
                "price": res.pop("ticket_price"),
                "currency": res.pop("ticket_currency"),
                "transport_type": res.pop("transport_type"),
                "class_type": res.pop("class_type"),
                "available_seats": res.pop("available_seats")
            }
        }
        
        if res["payment_id"]:
            formatted["payment_details"] = {
                "status": res.pop("payment_status"),
                "transaction_id": res.pop("transaction_id"),
                "payment_date": res.pop("payment_date")
            }
        
        formatted_reservations.append(formatted)
    
    return formatted_reservations

