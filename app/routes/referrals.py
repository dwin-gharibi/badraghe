from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
from app.db import connect_db, close_db, execute_query
from app.utils.auth_util import get_current_user

router = APIRouter(prefix="/referrals")

class ReferralCreate(BaseModel):
    referred_id: int

class ReferralOut(BaseModel):
    id: int
    referrer_id: int
    referred_id: int
    referred_at: datetime

class ReferralStats(BaseModel):
    referrer_id: int
    total_referrals: int
    latest_referral: Optional[datetime] = None

class ReferralUpdate(BaseModel):
    referred_id: Optional[int]

@router.post("/", response_model=ReferralOut, status_code=status.HTTP_201_CREATED)
async def create_referral(
    referral: ReferralCreate,
    current_user: dict = Depends(get_current_user)
):
    if referral.referred_id == current_user["user_id"]:
        raise HTTPException(status_code=400, detail="Cannot refer yourself")

    await connect_db()

    existing = await execute_query(
        """
        SELECT 1 FROM user_referrals 
        WHERE referrer_id = %s AND referred_id = %s
        """,
        (current_user["user_id"], referral.referred_id),
        fetch_one=True
    )
    if existing:
        await close_db()
        raise HTTPException(status_code=400, detail="Referral already exists")

    try:
        referral_id = await execute_query(
            """
            INSERT INTO user_referrals (referrer_id, referred_id)
            VALUES (%s, %s)
            """,
            (current_user["user_id"], referral.referred_id),
            fetch_one=True,
            return_lastrowid=True
        )
        referral_data = await execute_query(
            "SELECT * FROM user_referrals WHERE id = %s",
            (referral_id,),
            fetch_one=True
        )
        await close_db()
        return referral_data
    except Exception as e:
        await close_db()
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/", response_model=List[ReferralOut])
async def list_referrals(
    referrer_id: Optional[int] = None,
    referred_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 50,
    current_user: dict = Depends(get_current_user)
):
    await connect_db()
    query = "SELECT * FROM user_referrals WHERE 1=1"
    params = []

    if referrer_id:
        query += " AND referrer_id = %s"
        params.append(referrer_id)
    if referred_id:
        query += " AND referred_id = %s"
        params.append(referred_id)

    query += " ORDER BY referred_at DESC LIMIT %s OFFSET %s"
    params.extend([limit, skip])

    referrals = await execute_query(query, params, fetch_all=True)
    await close_db()
    return referrals

@router.get("/me", response_model=List[ReferralOut])
async def list_my_referrals(
    skip: int = 0,
    limit: int = 50,
    current_user: dict = Depends(get_current_user)
):
    await connect_db()
    referrals = await execute_query(
        """
        SELECT * FROM user_referrals 
        WHERE referrer_id = %s 
        ORDER BY referred_at DESC LIMIT %s OFFSET %s
        """,
        (current_user["user_id"], limit, skip),
        fetch_all=True
    )
    await close_db()
    return referrals

@router.get("/count", response_model=dict)
async def count_my_referrals(current_user: dict = Depends(get_current_user)):
    await connect_db()
    count_result = await execute_query(
        "SELECT COUNT(*) AS total FROM user_referrals WHERE referrer_id = %s",
        (current_user["user_id"],),
        fetch_one=True
    )
    await close_db()
    return {"referral_count": count_result["total"]}

@router.get("/stats/{referrer_id}", response_model=ReferralStats)
async def get_referral_stats(referrer_id: int):
    await connect_db()
    stats = await execute_query(
        """
        SELECT COUNT(*) AS total_referrals, MAX(referred_at) AS latest_referral
        FROM user_referrals WHERE referrer_id = %s
        """,
        (referrer_id,),
        fetch_one=True
    )
    await close_db()
    return {
        "referrer_id": referrer_id,
        "total_referrals": stats["total_referrals"],
        "latest_referral": stats["latest_referral"]
    }

@router.delete("/{referral_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_referral(
    referral_id: int,
    current_user: dict = Depends(get_current_user)
):
    await connect_db()
    referral = await execute_query(
        "SELECT * FROM user_referrals WHERE id = %s",
        (referral_id,),
        fetch_one=True
    )
    if not referral:
        await close_db()
        raise HTTPException(status_code=404, detail="Referral not found")

    if referral["referrer_id"] != current_user["user_id"]:
        await close_db()
        raise HTTPException(status_code=403, detail="Permission denied")

    await execute_query(
        "DELETE FROM user_referrals WHERE id = %s",
        (referral_id,),
        commit=True
    )
    await close_db()
    return

@router.get("/referred-users/{referrer_id}", response_model=List[dict])
async def get_referred_users(referrer_id: int):
    await connect_db()
    referred_users = await execute_query(
        """
        SELECT u.id, u.email, ur.referred_at
        FROM user_referrals ur
        JOIN users u ON ur.referred_id = u.id
        WHERE ur.referrer_id = %s
        ORDER BY ur.referred_at DESC
        """,
        (referrer_id,),
        fetch_all=True
    )
    await close_db()
    return referred_users

@router.get("/leaders", response_model=List[dict])
async def referral_leaderboard(limit: int = 10):
    await connect_db()
    leaderboard = await execute_query(
        """
        SELECT referrer_id, COUNT(*) as total
        FROM user_referrals
        GROUP BY referrer_id
        ORDER BY total DESC
        LIMIT %s
        """,
        (limit,),
        fetch_all=True
    )
    await close_db()
    return leaderboard

@router.get("/referred-by/{user_id}", response_model=Optional[ReferralOut])
async def who_referred_user(user_id: int):
    await connect_db()
    referral = await execute_query(
        "SELECT * FROM user_referrals WHERE referred_id = %s",
        (user_id,),
        fetch_one=True
    )
    await close_db()
    return referral

@router.get("/recent", response_model=List[ReferralOut])
async def recent_referrals(limit: int = 20):
    await connect_db()
    referrals = await execute_query(
        "SELECT * FROM user_referrals ORDER BY referred_at DESC LIMIT %s",
        (limit,),
        fetch_all=True
    )
    await close_db()
    return referrals

@router.patch("/{referral_id}", response_model=ReferralOut)
async def update_referral(
    referral_id: int,
    update: ReferralUpdate,
    current_user: dict = Depends(get_current_user)
):
    await connect_db()
    referral = await execute_query(
        "SELECT * FROM user_referrals WHERE id = %s",
        (referral_id,),
        fetch_one=True
    )
    if not referral:
        await close_db()
        raise HTTPException(status_code=404, detail="Referral not found")

    if referral["referrer_id"] != current_user["user_id"]:
        await close_db()
        raise HTTPException(status_code=403, detail="Permission denied")

    update_data = update.dict(exclude_unset=True)
    if not update_data:
        await close_db()
        raise HTTPException(status_code=400, detail="No fields to update")

    set_clause = ", ".join(f"{k} = %s" for k in update_data.keys())
    values = list(update_data.values()) + [referral_id]

    await execute_query(
        f"UPDATE user_referrals SET {set_clause} WHERE id = %s",
        values,
        commit=True
    )
    updated = await execute_query(
        "SELECT * FROM user_referrals WHERE id = %s",
        (referral_id,),
        fetch_one=True
    )
    await close_db()
    return updated

@router.head("/{referral_id}")
async def head_referral(referral_id: int):
    await connect_db()
    referral = await execute_query(
        "SELECT id FROM user_referrals WHERE id = %s",
        (referral_id,),
        fetch_one=True
    )
    await close_db()
    if not referral:
        raise HTTPException(status_code=404)
    return

@router.put("/{referral_id}", response_model=ReferralOut)
async def put_referral(
    referral_id: int,
    new_data: ReferralCreate,
    current_user: dict = Depends(get_current_user)
):
    await connect_db()
    referral = await execute_query(
        "SELECT * FROM user_referrals WHERE id = %s",
        (referral_id,),
        fetch_one=True
    )
    if not referral:
        await close_db()
        raise HTTPException(status_code=404, detail="Referral not found")

    if referral["referrer_id"] != current_user["user_id"]:
        await close_db()
        raise HTTPException(status_code=403, detail="Permission denied")

    await execute_query(
        "UPDATE user_referrals SET referred_id = %s WHERE id = %s",
        (new_data.referred_id, referral_id),
        commit=True
    )
    updated = await execute_query(
        "SELECT * FROM user_referrals WHERE id = %s",
        (referral_id,),
        fetch_one=True
    )
    await close_db()
    return updated