from datetime import datetime, timedelta, timezone
from fastapi import Query, APIRouter, Path, HTTPException, status, Depends, Header
from typing import Optional, List, Dict
from pydantic import BaseModel
from enum import Enum
from app.db import execute_query, connect_db, close_db
from app.utils.auth_util import get_current_user, require_roles
from app.utils.rbac_util import is_admin
import httpx
import uuid
import json
from app.utils.task_manager import schedule_reservation_cancellation

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

class ReservationUpdate(BaseModel):
    status: Optional[ReservationStatus] = None

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


@router.get("/stats", response_model=ReservationStatsResponse)
async def get_reservation_stats(
        transport_type: Optional[TransportType] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        current_user: dict = Depends(require_roles("admin"))
):
    where_clause = "WHERE 1=1"
    params = []

    if transport_type:
        where_clause += " AND t.transport_type = %s"
        params.append(transport_type.value)

    if start_date:
        where_clause += " AND r.reserved_at >= %s"
        params.append(start_date)

    if end_date:
        where_clause += " AND r.reserved_at <= %s"
        params.append(end_date)

    status_counts = await execute_query(
        f"""
        SELECT r.status, COUNT(*) as count
        FROM user_reservations r
        JOIN travel_tickets t ON r.ticket_id = t.id
        {where_clause}
        GROUP BY r.status
        """,
        params,
        fetch_all=True
    )

    transport_counts = await execute_query(
        f"""
        SELECT t.transport_type, COUNT(*) as count
        FROM user_reservations r
        JOIN travel_tickets t ON r.ticket_id = t.id
        {where_clause}
        GROUP BY t.transport_type
        """,
        params,
        fetch_all=True
    )

    stats = {
        "total_reservations": 0,
        "temporary": 0,
        "reserved": 0,
        "paid": 0,
        "canceled": 0,
        "by_transport_type": {}
    }

    for row in status_counts:
        stats["total_reservations"] += row["count"]
        stats[row["status"]] = row["count"]

    for row in transport_counts:
        stats["by_transport_type"][row["transport_type"]] = row["count"]

    return stats


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
            reserved_at
        ) VALUES (%s, %s, 'temporary', %s)
        """,
        (
            current_user["user_id"],
            reservation.ticket_id,
            reserved_at,
        ),
        fetch_one=True,
        return_lastrowid=True
    )

    await execute_query(
        "UPDATE travel_tickets SET available_seats = available_seats - 1 WHERE id = %s",
        (reservation.ticket_id,),
        commit=True
    )
    schedule_reservation_cancellation(reservation_id, delay_seconds=60)
    await close_db()
    return await get_reservation_details(reservation_id)

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
        not await has_permission(current_user["user_id"], "view_all:reservations") and not is_admin(current_user["user_id"])):
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
    
    if not await has_permission(current_user["user_id"], "view_all:reservations") and not is_admin(current_user["user_id"]):
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
        not await has_permission(current_user["user_id"], "manage_all:reservations") and not is_admin(current_user["user_id"])):
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
        not await has_permission(current_user["user_id"], "delete_all:reservations") and not is_admin(current_user["user_id"])):
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
            
            payment_details_json = json.dumps({"payment_url": payment_url, "gateway": "zarinpal"})

            payment_id = await execute_query(
                """
                INSERT INTO payments (
                    user_id, reservation_id, amount,
                    payment_method_id, status, transaction_id,
                    currency, payment_details
                ) VALUES (%s, %s, %s, %s, 'pending', %s, %s, %s)
                """,
                (
                    current_user["user_id"],
                    reservation_id,
                    payment.amount,
                    payment.payment_method_id,
                    authority,
                    payment.currency,
                    payment_details_json
                ),
                return_lastrowid=True
            )

            return {
                "payment_url": payment_url,
                "payment_id": payment_id,
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
            """,
            (
                current_user["user_id"],
                reservation_id,
                payment.amount,
                payment.payment_method_id,
                transaction_id,
                payment.currency
            ),
            fetch_one=True,
            return_lastrowid=True
        )
        
        await execute_query(
            """
            UPDATE user_reservations 
            SET status = 'paid', payment_id = %s 
            WHERE id = %s
            """,
            (payment_id, reservation_id),
            commit=True
        )
        
        return {
            "payment_id": payment_id,
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

@router.get("/user/{user_id}/history", response_model=List[ReservationResponse])
async def get_user_reservation_history(
    user_id: int,
    reservation_status: Optional[ReservationStatus] = None,
    transport_type: Optional[TransportType] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    skip: int = 0,
    limit: int = 100,
    current_user: dict = Depends(get_current_user)
):
    if user_id != current_user["user_id"] and not await has_permission(current_user["user_id"], "view_all:reservations") and not is_admin(current_user["user_id"]):
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
    
    if reservation_status:
        query += " AND r.status = %s"
        params.append(reservation_status.value)
    
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

async def has_permission(user_id: int, permission: str) -> bool:
    return await execute_query(
        """
        SELECT 1 FROM user_role ur
        JOIN role_permissions rp ON ur.role_id = rp.role_id
        JOIN permissions p ON rp.permission_id = p.id
        WHERE ur.user_id = %s AND p.name = %s
        """,
        (user_id, permission),
        fetch_one=True
    ) is not None

@router.get("/penalty/{reservation_id}", response_model=dict)
async def get_cancellation_penalty(reservation_id: int, current_user: dict = Depends(get_current_user)):

    reservation = await execute_query(
        """
        SELECT tt.departure_time, tt.transport_company_id
        FROM user_reservations ur
        JOIN travel_tickets tt ON ur.ticket_id = tt.id
        WHERE ur.id = %s
        """,
        (reservation_id,),
        fetch_one=True
    )

    if not reservation:
        raise HTTPException(status_code=404, detail="Reservation not found")

    departure_time = reservation["departure_time"]

    if isinstance(departure_time, str):
        departure_time = datetime.fromisoformat(departure_time)

    if departure_time.tzinfo is None:
        departure_time = departure_time.replace(tzinfo=timezone.utc)

    now = datetime.now(timezone.utc)
    hours_left = (departure_time - now).total_seconds() / 3600

    provider = await execute_query(
        "SELECT cancellation_penalty FROM service_providers WHERE id = %s",
        (reservation["transport_company_id"],),
        fetch_one=True
    )

    if not provider:
        raise HTTPException(status_code=404, detail="Service provider not found")

    base_penalty = float(provider["cancellation_penalty"] or 0)

    if hours_left < 1:
        penalty_percent = base_penalty
    elif hours_left < 12:
        penalty_percent = base_penalty / 2
    else:
        penalty_percent = 0

    return {
        "penalty_percent": round(penalty_percent, 2),
        "hours_until_departure": round(hours_left, 2),
        "base_penalty_percent": base_penalty
    }

@router.post("/cancel/{reservation_id}/")
async def user_cancel_reservation(
    user_id: int,
    reservation_id: int,
    cancellation_reason: str,
    current_user=Depends(get_current_user),
):
    if current_user["user_id"] != user_id:
        roles = await execute_query(
            """
            SELECT r.name 
            FROM user_role ur 
            JOIN roles r ON ur.role_id = r.id 
            WHERE ur.user_id = %s
            """,
            (current_user["user_id"],),
            fetch_all=True,
        )
        user_roles = [r["name"] if isinstance(r, dict) else r[0] for r in roles] if roles else []
        if "admin" not in user_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to cancel other users' reservations",
            )

    await connect_db()

    reservation = await execute_query(
        """
        SELECT ur.*, tt.departure_time, tt.transport_company_id
        FROM user_reservations ur
        JOIN travel_tickets tt ON ur.ticket_id = tt.id
        WHERE ur.id = %s AND ur.user_id = %s
        """,
        (reservation_id, user_id),
        fetch_one=True,
    )

    if not reservation:
        await close_db()
        raise HTTPException(status_code=404, detail="Reservation not found or does not belong to user")

    departure_time = reservation["departure_time"]
    if isinstance(departure_time, str):
        departure_time = datetime.fromisoformat(departure_time)

    if departure_time.tzinfo is None:
        departure_time = departure_time.replace(tzinfo=timezone.utc)

    now = datetime.now(timezone.utc)
    hours_left = (departure_time - now).total_seconds() / 3600

    provider = await execute_query(
        "SELECT cancellation_penalty FROM service_providers WHERE id = %s",
        (reservation["transport_company_id"],),
        fetch_one=True
    )

    if not provider:
        await close_db()
        raise HTTPException(status_code=404, detail="Service provider not found")

    base_penalty = float(provider["cancellation_penalty"] or 0)

    if hours_left < 1:
        penalty_percent = base_penalty
    elif hours_left < 12:
        penalty_percent = base_penalty / 2
    else:
        penalty_percent = 0

    await execute_query(
        """
        INSERT INTO ticket_cancellations 
            (reservation_id, canceled_by, cancellation_reason, canceled_at, created_at, updated_at)
        VALUES (%s, %s, %s, NOW(), NOW(), NOW())
        """,
        (reservation_id, user_id, cancellation_reason),
    )

    await execute_query(
        """
        UPDATE user_reservations 
        SET status = 'canceled', refund_status = 'pending', updated_at = NOW()
        WHERE id = %s
        """,
        (reservation_id,),
    )

    price_paid = float(reservation.get("price_paid") or 0)
    refund_amount = price_paid * (100 - penalty_percent) / 100

    if reservation["status"] == "paid":
        await execute_query(
            """
            INSERT INTO refund_requests 
                (user_id, payment_id, reason, status, refund_amount, request_date, created_at, updated_at)
            VALUES (%s, %s, %s, 'pending', %s, NOW(), NOW(), NOW())
            """,
            (user_id, reservation["payment_id"], cancellation_reason, refund_amount),
        )

    await close_db()

    return {
        "message": "Ticket canceled successfully and refund request submitted",
        "refund_amount": round(refund_amount, 2),
        "penalty_percent": round(penalty_percent, 2),
        "hours_until_departure": round(hours_left, 2),
    }
