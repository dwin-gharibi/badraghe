from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel
from app.db import execute_query, connect_db
from app.utils.auth_util import get_current_user, require_roles

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
            RETURNING id
            """,
            (
                discount.code, discount.discount_type, discount.discount_value,
                discount.valid_from, discount.valid_until, discount.status
            ),
            fetch_one=True
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

