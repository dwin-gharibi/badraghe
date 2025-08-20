from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional, Dict
from datetime import datetime
from pydantic import BaseModel
from app.db import execute_query, connect_db, close_db
from app.utils.auth_util import require_roles, get_current_user
import httpx
from fastapi.responses import RedirectResponse

router = APIRouter(prefix="/payments")

class PaymentCreate(BaseModel):
    reservation_id: int
    payment_method_id: int
    amount: float
    currency: str = "IRR"

class PaymentStatusUpdate(BaseModel):
    status: str

class RefundAction(BaseModel):
    action: str

class PaymentUpdate(BaseModel):
    amount: Optional[float] = None
    currency: Optional[str] = None
    payment_method_id: Optional[int] = None

class FullPaymentUpdate(BaseModel):
    user_id: int
    reservation_id: int
    amount: float
    currency: str
    payment_method_id: int
    status: str
    transaction_id: str

@router.get("/count", response_model=Dict[str, int])
async def get_payment_count(
    current_user: dict = Depends(get_current_user),
    user_id: int = None
):
    await connect_db()
    query = """
        SELECT COUNT(*) as count
        FROM payments p
        WHERE p.user_id = %s
    """
    params = (current_user["user_id"],)
    if user_id:
        query += " AND p.user_id = %s"
        params = (current_user["user_id"], user_id)
    
    result = await execute_query(query, params, fetch_one=True)
    await close_db()
    return {"count": result["count"]}


@router.get("/refunds", response_model=List[dict])
async def list_refund_requests(current_user: dict = Depends(get_current_user)):
    await connect_db()
    refunds = await execute_query(
        """
        SELECT rr.id, rr.reason, rr.status, rr.refund_amount,
               rr.created_at, p.id as payment_id
        FROM refund_requests rr
        JOIN payments p ON rr.payment_id = p.id
        WHERE rr.user_id = %s
        ORDER BY rr.created_at DESC
        """,
        (current_user["user_id"],),
        fetch_all=True
    )
    await close_db()
    return refunds

@router.get("/refunds/count", response_model=Dict[str, int])
async def get_refund_request_count(
    current_user: dict = Depends(get_current_user),
    user_id: int = None
):
    await connect_db()
    query = """
        SELECT COUNT(*) as count
        FROM refund_requests rr
        WHERE rr.user_id = %s
    """
    params = (current_user["user_id"],)
    if user_id:
        query += " AND rr.user_id = %s"
        params = (current_user["user_id"], user_id)
    
    result = await execute_query(query, params, fetch_one=True)
    await close_db()
    return {"count": result["count"]}

@router.post("/refunds/{refund_id}/action", dependencies=[Depends(require_roles("admin"))])
async def handle_refund(refund_id: int, action_data: RefundAction):
    await connect_db()

    if action_data.action not in ["approved", "rejected"]:
        raise HTTPException(status_code=400, detail="Invalid action")

    status = "approved" if action_data.action == "approved" else "rejected"

    refund = await execute_query(
        """
        SELECT user_id, refund_amount FROM refund_requests
        WHERE id = %s
        """,
        (refund_id,),
        fetch_one=True
    )

    if not refund:
        raise HTTPException(status_code=404, detail="Refund request not found")

    await execute_query(
        """
        UPDATE refund_requests
        SET status = %s, updated_at = NOW(), processed_at = NOW()
        WHERE id = %s
        """,
        (status, refund_id),
        commit=True
    )

    if status == "approved":
        await execute_query(
            """
            UPDATE users
            SET balance = balance + %s
            WHERE id = %s
            """,
            (refund["refund_amount"], refund["user_id"]),
            commit=True
        )

    await close_db()

    return {"message": f"Refund request {status}"}

@router.get("/methods", response_model=List[dict])
async def get_payment_methods():
    await connect_db()
    methods = await execute_query(
        "SELECT id, name, description, is_active FROM payment_methods WHERE is_active = TRUE",
        fetch_all=True
    )
    await close_db()
    return methods

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_payment(
    payment: PaymentCreate,
    current_user: dict = Depends(get_current_user)
):
    await connect_db()
    reservation = await execute_query(
        """
        SELECT id, user_id, status, price_paid 
        FROM user_reservations 
        WHERE id = %s
        """,
        (payment.reservation_id,),
        fetch_one=True
    )
    if not reservation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reservation not found"
        )
    
    if reservation["user_id"] != current_user["user_id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to pay for this reservation"
        )
    
    if reservation["status"] != "temporary":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Reservation is not in a payable state"
        )
    
    method = await execute_query(
        "SELECT 1 FROM payment_methods WHERE id = %s AND is_active = TRUE",
        (payment.payment_method_id,),
        fetch_one=True
    )
    if not method:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid payment method"
        )
    print(abs(float(reservation["price_paid"]) - float(payment.amount)))
    if abs(float(reservation["price_paid"]) - float(payment.amount)) < 0.0001:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Payment amount doesn't match reservation total"
        )
    
    try:
        transaction_id = f"txn_{int(datetime.now().timestamp())}_{payment.reservation_id}"
        
        payment_id = await execute_query(
            """
            INSERT INTO payments (
                user_id, reservation_id, amount,
                payment_method_id, status, transaction_id, currency
            ) VALUES (%s, %s, %s, %s, 'successful', %s, %s)
            """,
            (
                current_user["user_id"],
                payment.reservation_id,
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
            SET status = 'paid', payment_id = %s, price_paid = %s
            WHERE id = %s
            """,
            (payment_id, payment.reservation_id, payment.amount),
            commit=True
        )

        await close_db()
        return {
            "payment_id": payment_id,
            "transaction_id": transaction_id,
            "status": "successful"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/user", response_model=List[dict])
async def get_user_payments(
    skip: int = 0,
    limit: int = 100,
    current_user: dict = Depends(get_current_user)
):
    await connect_db()
    payments = await execute_query(
        """
        SELECT p.id, p.amount, p.currency, p.status,
               p.transaction_id, p.payment_date,
               pm.name as payment_method,
               r.id as reservation_id
        FROM payments p
        JOIN payment_methods pm ON p.payment_method_id = pm.id
        JOIN user_reservations r ON p.reservation_id = r.id
        WHERE p.user_id = %s
        ORDER BY p.payment_date DESC
        LIMIT %s OFFSET %s
        """,
        (current_user["user_id"], limit, skip),
        fetch_all=True
    )
    await close_db()
    return payments

@router.post("/{payment_id}/refund", status_code=status.HTTP_200_OK)
async def request_refund(
    payment_id: int,
    reason: str,
    current_user: dict = Depends(get_current_user)
):
    await connect_db()
    payment = await execute_query(
        """
        SELECT id, user_id, amount, status, refund_amount
        FROM payments
        WHERE id = %s
        """,
        (payment_id,),
        fetch_one=True
    )
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found"
        )
    
    if payment["user_id"] != current_user["user_id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to request refund for this payment"
        )
    
    if payment["status"] != "successful":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only successful payments can be refunded"
        )
    
    if float(payment["refund_amount"]) > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Refund already processed for this payment"
        )
    
    try:
        refund_id = await execute_query(
            """
            INSERT INTO refund_requests (
                user_id, payment_id, reason,
                status, refund_amount
            ) VALUES (%s, %s, %s, 'pending', %s)
            """,
            (
                current_user["user_id"],
                payment_id,
                reason,
                payment["amount"]
            ),
            fetch_one=True,
            return_lastrowid=True
        )
        await close_db()
        return {"refund_id": refund_id, "status": "pending"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_payment(id: int, db=Depends(get_current_user)):
    try:
        await connect_db()
        await execute_query("""
                    DELETE FROM payments WHERE id = %s
                """, (id,))
        await connect_db()
        HTTPException(status_code=200, detail="Payment successfuly removed")
    except Exception as e:
        raise HTTPException(status_code=404, detail="Payment not found")
    
ZARINPAL_VERIFY_API = "https://sandbox.zarinpal.com/pg/v4/payment/verify.json"
ZARINPAL_MERCHANT_ID = "XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX"
ZARINPAL_API = "https://sandbox.zarinpal.com/pg/v4/payment/request.json"

@router.get("/verify")
async def verify_payment(
    reservation_id: int,
    user_id: int,
    Authority: str = Query(..., alias="Authority"),
    Status: str = Query(..., alias="Status"),
):
    await connect_db()

    if Status != "OK":
        raise HTTPException(status_code=400, detail="Payment was canceled or failed")

    payment = await execute_query(
        "SELECT * FROM payments WHERE transaction_id = %s AND status = 'pending'", (Authority,), fetch_one=True
    )

    if not payment:
        raise HTTPException(status_code=404, detail="Pending payment not found")

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
            "UPDATE payments SET status = 'successful', updated_at = NOW() WHERE id = %s", (payment["id"],)
        )
        await execute_query(
            "UPDATE user_reservations SET status = 'paid', payment_id = %s, updated_at = NOW() WHERE id = %s",
            (payment["id"], reservation_id)
        )
        return RedirectResponse(url=f"https://badraghe.dwin.codes/user/reservations")
    else:
        await execute_query(
            "UPDATE payments SET status = 'failed', updated_at = NOW() WHERE id = %s", (payment["id"],)
        )
        raise HTTPException(status_code=400, detail="Payment verification failed")
    
@router.get("/{payment_id}")
async def get_payment_by_id(payment_id: int, current_user: dict = Depends(get_current_user)):
    await connect_db()
    payment = await execute_query(
        """
        SELECT p.id, p.amount, p.currency, p.status,
               p.transaction_id, p.payment_date,
               pm.name as payment_method,
               r.id as reservation_id
        FROM payments p
        JOIN payment_methods pm ON p.payment_method_id = pm.id
        JOIN user_reservations r ON p.reservation_id = r.id
        WHERE p.id = %s
        """,
        (payment_id),
        fetch_one=True,
    )

    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    
    await close_db()
    return payment

@router.put("/{payment_id}/status", dependencies=[Depends(require_roles("admin"))])
async def update_payment_status(payment_id: int, status_update: PaymentStatusUpdate):
    await connect_db()
    if status_update.status not in ["pending", "successful", "failed", "refunded"]:
        raise HTTPException(status_code=400, detail="Invalid status")

    await execute_query(
        "UPDATE payments SET status = %s, updated_at = NOW() WHERE id = %s",
        (status_update.status, payment_id),
        commit=True
    )
    await close_db()
    return {"message": "Payment status updated successfully"}

@router.get("/", dependencies=[Depends(require_roles("admin"))], response_model=List[dict])
async def get_all_payments(skip: int = 0, limit: int = 100):
    await connect_db()
    payments = await execute_query(
        """
        SELECT p.id, p.amount, p.currency, p.status,
               p.transaction_id, p.payment_date,
               u.email, r.id as reservation_id
        FROM payments p
        JOIN users u ON p.user_id = u.id
        JOIN user_reservations r ON p.reservation_id = r.id
        ORDER BY p.payment_date DESC
        LIMIT %s OFFSET %s
        """,
        (limit, skip),
        fetch_all=True
    )

    await close_db()
    return payments

@router.patch("/{payment_id}", dependencies=[Depends(require_roles("admin"))])
async def patch_payment(payment_id: int, update_data: PaymentUpdate):
    
    await connect_db()

    fields = []
    values = []

    for field, value in update_data.dict(exclude_none=True).items():
        fields.append(f"{field} = %s")
        values.append(value)

    if not fields:
        raise HTTPException(status_code=400, detail="No valid fields provided for update")

    query = f"""
        UPDATE payments SET {', '.join(fields)}, updated_at = NOW()
        WHERE id = %s
    """
    values.append(payment_id)

    await execute_query(query, tuple(values), commit=True)
    await close_db()

    return {"message": "Payment updated successfully"}

@router.put("/{payment_id}", dependencies=[Depends(require_roles("admin"))])
async def replace_payment(payment_id: int, data: FullPaymentUpdate):
    await connect_db()
    await execute_query(
        """
        UPDATE payments SET user_id = %s, reservation_id = %s, amount = %s, 
            currency = %s, payment_method_id = %s, status = %s, transaction_id = %s, updated_at = NOW()
        WHERE id = %s
        """,
        (
            data.user_id, data.reservation_id, data.amount,
            data.currency, data.payment_method_id, data.status,
            data.transaction_id, payment_id
        ),
        commit=True
    )
    await close_db()
    return {"message": "Payment record replaced"}

@router.head("/{payment_id}")
async def check_payment_exists(payment_id: int):
    await connect_db()
    payment = await execute_query(
        "SELECT 1 FROM payments WHERE id = %s", (payment_id,), fetch_one=True
    )
    if not payment:
        raise HTTPException(status_code=404)
    
    await close_db()
