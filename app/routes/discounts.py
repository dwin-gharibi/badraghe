from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel
from app.db import execute_query, connect_db
from app.utils.auth_util import get_current_user, require_roles
from app.utils.rbac_util import has_permission

router = APIRouter(prefix="/discounts")

class DiscountCreate(BaseModel):
    code: str
    discount_type: str
    discount_value: float
    valid_from: datetime
    valid_until: datetime
    status: bool = True

class DiscountUpdate(BaseModel):
    code: Optional[str] = None
    discount_type: Optional[str] = None
    discount_value: Optional[float] = None
    valid_from: Optional[datetime] = None
    valid_until: Optional[datetime] = None
    status: Optional[bool] = None

class LoyaltyPointsUpdate(BaseModel):
    points: int

async def _get_discount(discount_id: int):
    discount = await execute_query(
        "SELECT * FROM discounts WHERE id = %s",
        (discount_id,),
        fetch_one=True
    )
    if not discount:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Discount not found"
        )
    return discount

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_discount(
    discount: DiscountCreate,
    current_user: dict = Depends(require_roles("admin"))
):
    valid_types = ["percentage", "fixed"]
    if discount.discount_type not in valid_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid discount type. Must be one of: {', '.join(valid_types)}"
        )

    if discount.discount_type == "percentage" and not (0 <= discount.discount_value <= 100):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Percentage discount must be between 0 and 100"
        )
    elif discount.discount_type == "fixed" and discount.discount_value <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Fixed discount must be greater than 0"
        )

    existing = await execute_query(
        "SELECT 1 FROM discounts WHERE code = %s",
        (discount.code,),
        fetch_one=True
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Discount with this code already exists"
        )

    try:
        discount_id = await execute_query(
            """
            INSERT INTO discounts (
                code, discount_type, discount_value,
                valid_from, valid_until, status
            ) VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (
                discount.code, discount.discount_type, discount.discount_value,
                discount.valid_from, discount.valid_until, discount.status
            ),
            fetch_one=True,
            return_lastrowid=True
        )
        return {"discount_id": discount_id["id"]}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/", response_model=List[dict])
async def get_discounts(
    active_only: bool = True,
    code: Optional[str] = None,
    discount_type: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    current_user: dict = Depends(get_current_user)
):
    query = "SELECT * FROM discounts WHERE 1=1"
    params = []
    
    if active_only:
        query += " AND status = TRUE AND valid_from <= NOW() AND valid_until >= NOW()"
    
    if code:
        query += " AND code LIKE %s"
        params.append(f"%{code}%")
    
    if discount_type:
        query += " AND discount_type = %s"
        params.append(discount_type)
    
    query += " ORDER BY valid_from DESC LIMIT %s OFFSET %s"
    params.extend([limit, skip])
    
    discounts = await execute_query(query, params, fetch_all=True)
    return discounts

@router.get("/{discount_id}", response_model=dict)
async def get_discount(
    discount_id: int,
    current_user: dict = Depends(get_current_user)
):
    return await _get_discount(discount_id)

@router.put("/{discount_id}", response_model=dict)
async def update_discount(
    discount_id: int,
    discount: DiscountCreate,
    current_user: dict = Depends(require_roles("admin"))
):
    valid_types = ["percentage", "fixed"]
    if discount.discount_type not in valid_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid discount type. Must be one of: {', '.join(valid_types)}"
        )

    if discount.discount_type == "percentage" and not (0 <= discount.discount_value <= 100):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Percentage discount must be between 0 and 100"
        )
    elif discount.discount_type == "fixed" and discount.discount_value <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Fixed discount must be greater than 0"
        )

    existing = await execute_query(
        "SELECT 1 FROM discounts WHERE code = %s AND id != %s",
        (discount.code, discount_id),
        fetch_one=True
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Discount with this code already exists"
        )

    try:
        await execute_query(
            """
            UPDATE discounts 
            SET code = %s, discount_type = %s, discount_value = %s,
                valid_from = %s, valid_until = %s, status = %s
            WHERE id = %s
            """,
            (
                discount.code, discount.discount_type, discount.discount_value,
                discount.valid_from, discount.valid_until, discount.status, discount_id
            ),
            commit=True
        )
        return await _get_discount(discount_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.patch("/{discount_id}", response_model=dict)
async def partial_update_discount(
    discount_id: int,
    discount: DiscountUpdate,
    current_user: dict = Depends(require_roles("admin"))
):
    update_data = discount.dict(exclude_unset=True)
    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields to update"
        )

    if "discount_type" in update_data:
        valid_types = ["percentage", "fixed"]
        if update_data["discount_type"] not in valid_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid discount type. Must be one of: {', '.join(valid_types)}"
            )

    if "discount_value" in update_data:
        if "discount_type" in update_data:
            discount_type = update_data["discount_type"]
        else:
            current_discount = await _get_discount(discount_id)
            discount_type = current_discount["discount_type"]
        
        if discount_type == "percentage" and not (0 <= update_data["discount_value"] <= 100):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Percentage discount must be between 0 and 100"
            )
        elif discount_type == "fixed" and update_data["discount_value"] <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Fixed discount must be greater than 0"
            )

    if "code" in update_data:
        existing = await execute_query(
            "SELECT 1 FROM discounts WHERE code = %s AND id != %s",
            (update_data["code"], discount_id),
            fetch_one=True
        )
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Discount with this code already exists"
            )

    set_clause = ", ".join([f"{field} = %s" for field in update_data.keys()])
    values = list(update_data.values())
    values.append(discount_id)

    try:
        await execute_query(
            f"UPDATE discounts SET {set_clause} WHERE id = %s",
            values,
            commit=True
        )
        return await _get_discount(discount_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.delete("/{discount_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_discount(
    discount_id: int,
    current_user: dict = Depends(require_roles("admin"))
):
    affected = await execute_query(
        "DELETE FROM discounts WHERE id = %s",
        (discount_id,),
        commit=True
    )
    if not affected:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Discount not found"
        )

@router.post("/apply-to-ticket", status_code=status.HTTP_200_OK)
async def apply_discount_to_ticket(
    ticket_id: int,
    discount_id: int,
    current_user: dict = Depends(require_roles("admin"))
):
    ticket = await execute_query(
        "SELECT 1 FROM travel_tickets WHERE id = %s",
        (ticket_id,),
        fetch_one=True
    )
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found"
        )
    
    discount = await execute_query(
        """
        SELECT 1 FROM discounts 
        WHERE id = %s AND status = TRUE 
        AND valid_from <= NOW() AND valid_until >= NOW()
        """,
        (discount_id,),
        fetch_one=True
    )
    if not discount:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Discount not valid or expired"
        )
    
    try:
        await execute_query(
            "INSERT IGNORE INTO ticket_discounts (ticket_id, discount_id) VALUES (%s, %s)",
            (ticket_id, discount_id),
            commit=True
        )
        return {"message": "Discount applied to ticket"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.delete("/remove-from-ticket", status_code=status.HTTP_200_OK)
async def remove_discount_from_ticket(
    ticket_id: int,
    discount_id: int,
    current_user: dict = Depends(require_roles("admin"))
):
    affected = await execute_query(
        "DELETE FROM ticket_discounts WHERE ticket_id = %s AND discount_id = %s",
        (ticket_id, discount_id),
        commit=True
    )
    if not affected:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Discount not applied to this ticket"
        )
    return {"message": "Discount removed from ticket"}

@router.get("/ticket/{ticket_id}", response_model=List[dict])
async def get_ticket_discounts(
    ticket_id: int,
    current_user: dict = Depends(get_current_user)
):
    discounts = await execute_query(
        """
        SELECT d.*
        FROM ticket_discounts td
        JOIN discounts d ON td.discount_id = d.id
        WHERE td.ticket_id = %s
        AND d.status = TRUE 
        AND d.valid_from <= NOW() 
        AND d.valid_until >= NOW()
        """,
        (ticket_id,),
        fetch_all=True
    )
    return discounts

@router.get("/user-loyalty/{user_id}", response_model=dict)
async def get_user_loyalty(
    user_id: int,
    current_user: dict = Depends(get_current_user)
):
    if current_user["user_id"] != user_id and not await has_permission(current_user["user_id"], "read:loyalty"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this loyalty information"
        )
    
    loyalty = await execute_query(
        "SELECT * FROM user_loyalty WHERE user_id = %s",
        (user_id,),
        fetch_one=True
    )
    if not loyalty:
        return {"user_id": user_id, "total_points": 0}
    return loyalty

@router.post("/user-loyalty/{user_id}/add-points", status_code=status.HTTP_200_OK)
async def add_loyalty_points(
    user_id: int,
    points: LoyaltyPointsUpdate,
    current_user: dict = Depends(require_roles("admin"))
):
    if points.points <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Points must be greater than 0"
        )
    
    try:
        await execute_query(
            """
            INSERT INTO user_loyalty (user_id, total_points, last_transaction)
            VALUES (%s, %s, NOW())
            ON DUPLICATE KEY UPDATE 
            total_points = total_points + VALUES(total_points),
            last_transaction = VALUES(last_transaction)
            """,
            (user_id, points.points),
            commit=True
        )
        return {"message": f"Added {points.points} loyalty points to user"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/user-loyalty/{user_id}/redeem", status_code=status.HTTP_200_OK)
async def redeem_loyalty_points(
    user_id: int,
    points: LoyaltyPointsUpdate,
    current_user: dict = Depends(get_current_user)
):
    if current_user["user_id"] != user_id and not await has_permission(current_user["user_id"], "update:loyalty"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to redeem points for this user"
        )
    
    if points.points <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Points must be greater than 0"
        )
    
    loyalty = await execute_query(
        "SELECT total_points FROM user_loyalty WHERE user_id = %s",
        (user_id,),
        fetch_one=True
    )
    if not loyalty or loyalty["total_points"] < points.points:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Not enough loyalty points"
        )
    
    try:
        await execute_query(
            """
            UPDATE user_loyalty 
            SET total_points = total_points - %s,
                last_transaction = NOW()
            WHERE user_id = %s
            """,
            (points.points, user_id),
            commit=True
        )
        return {"message": f"Redeemed {points.points} loyalty points"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )