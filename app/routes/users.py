from fastapi import APIRouter, Depends, HTTPException, status, Body
from typing import List, Optional
from app.db import execute_query, close_db, connect_db
from app.utils.auth_util import get_current_user, require_roles
from app.utils.rbac_util import has_permission, is_admin
from pydantic import BaseModel, Field
from typing import Optional
from datetime import date, datetime
from app.utils.cache_util import get_cache, set_cache, delete_cache
import json

router = APIRouter(prefix="/users")
CACHE_TTL = 600

class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    country: Optional[str] = None
    state: Optional[str] = None
    city: Optional[str] = None
    address: Optional[str] = None
    zip_code: Optional[str] = None
    date_of_birth: Optional[date] = None
    gender: Optional[str] = None
    bio: Optional[str] = None

def serialize_dates(obj):
    if isinstance(obj, dict):
        return {k: serialize_dates(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [serialize_dates(i) for i in obj]
    elif isinstance(obj, (datetime, date)):
        return obj.isoformat()
    else:
        return obj
    
@router.get("/profile", response_model=dict)
async def get_my_profile(
    current_user: dict = Depends(get_current_user)
):
    user_id = current_user["user_id"]
    cache_key = f"user_profile:{user_id}"

    cached = await get_cache(cache_key)
    if cached:
        return json.loads(cached)

    await connect_db()
    user = await execute_query(
        """
        SELECT id, first_name, last_name, email, phone, balance,
               country, state, city, address, zip_code,
               date_of_birth, gender, profile_picture_url,
               status, is_verified, bio, preferences,
               last_login, created_at
        FROM users 
        WHERE id = %s
        """,
        (user_id,),
        fetch_one=True
    )
    await close_db()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    await set_cache(cache_key, json.dumps(user, default=serialize_dates), expire_seconds=CACHE_TTL)

    return user


@router.put("/profile", response_model=dict)
async def update_my_profile(
    profile_update: dict = Body(...),
    current_user: dict = Depends(get_current_user)
):
    user_id = current_user["user_id"]

    allowed_fields = {
        "first_name", "last_name", "phone",
        "country", "state", "city", "address", "zip_code",
        "date_of_birth", "gender", "profile_picture_url",
        "bio", "preferences"
    }

    update_data = {k: v for k, v in profile_update.items() if k in allowed_fields}
    if not update_data:
        raise HTTPException(status_code=400, detail="No valid fields to update")

    set_clause = ", ".join(f"{k} = %s" for k in update_data)
    values = list(update_data.values())
    values.append(user_id)

    await connect_db()
    await execute_query(
        f"UPDATE users SET {set_clause} WHERE id = %s",
        values,
        commit=True
    )

    cache_key = f"user_profile:{user_id}"
    await delete_cache(cache_key)

    user = await execute_query(
        """
        SELECT id, first_name, last_name, email, phone, balance,
               country, state, city, address, zip_code,
               date_of_birth, gender, profile_picture_url,
               status, is_verified, bio, preferences,
               last_login, created_at
        FROM users 
        WHERE id = %s
        """,
        (user_id,),
        fetch_one=True
    )
    await set_cache(cache_key, json.dumps(user, default=serialize_dates), expire_seconds=CACHE_TTL)
    
    await close_db()

    return user

@router.get("/", response_model=List[dict])
async def get_users(
    skip: int = 0,
    limit: int = 100,
    current_user: dict = Depends(require_roles("admin"))
):
    try:
        await connect_db()
        users = await execute_query(
            """
            SELECT id, first_name, last_name, email, phone, status, is_verified, created_at 
            FROM users 
            LIMIT %s OFFSET %s
            """,
            (limit, skip),
            fetch_all=True
        )
        await close_db()
        return users
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/{user_id}", response_model=dict)
async def get_user(
    user_id: int,
    current_user: dict = Depends(get_current_user)
):
    if current_user["user_id"] != user_id and not await has_permission(current_user["user_id"], "read:users") and not is_admin(current_user["user_id"]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this user"
        )

    await connect_db()
    user = await execute_query(
        """
        SELECT id, first_name, last_name, email, phone, 
               country, state, city, address, zip_code,
               date_of_birth, gender, profile_picture_url,
               status, is_verified, bio, preferences, balance,
               last_login, created_at
        FROM users 
        WHERE id = %s
        """,
        (user_id,),
        fetch_one=True
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    await close_db()
    return user

@router.put("/{user_id}", response_model=dict)
async def update_user(
    user_id: int,
    update_data: UserUpdate = Body(...),
    current_user: dict = Depends(get_current_user)
):
    if current_user["user_id"] != user_id and not await has_permission(current_user["user_id"], "update:users") and not is_admin(current_user["user_id"]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this user"
        )

    await connect_db()
    update_dict = update_data.dict(exclude_unset=True)
    
    allowed_fields = {
        "first_name", "last_name", "country", "state", "city",
        "address", "zip_code", "date_of_birth", "gender", "bio"
    }

    if not await has_permission(current_user["user_id"], "update:users"):
        update_dict = {k: v for k, v in update_dict.items() if k in allowed_fields}

    if not update_dict:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No valid fields to update"
        )

    set_clause = ", ".join([f"{field} = %s" for field in update_dict.keys()])
    values = list(update_dict.values())
    values.append(user_id)

    try:
        await execute_query(
            f"UPDATE users SET {set_clause} WHERE id = %s",
            tuple(values),
            commit=True
        )
        return await get_user(user_id, current_user)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
@router.delete("/{user_id}", status_code=status.HTTP_200_OK)
async def delete_user(
    user_id: int,
    current_user: dict = Depends(require_roles("admin"))
):
    if current_user["user_id"] == user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account"
        )
    
    await connect_db()
    try:
        affected = await execute_query(
            "DELETE FROM users WHERE id = %s",
            (user_id,),
            return_rowcount=True
        )
        if affected == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
    finally:
        await close_db()

    return {"message": "User deleted successfully"}

@router.patch("/{user_id}/status", status_code=status.HTTP_200_OK)
async def update_user_status(
    user_id: int,
    user_status: bool,
    current_user: dict = Depends(require_roles("admin"))
):
    await connect_db()
    affected = await execute_query(
        "UPDATE users SET status = %s WHERE id = %s",
        (user_status, user_id),
        return_rowcount=True
    )
    await close_db()

    if affected == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return {"message": f"User status set to {user_status}"}


@router.patch("/{user_id}/balance", status_code=status.HTTP_200_OK)
async def update_user_status(
    user_id: int,
    user_balance: int,
    current_user: dict = Depends(require_roles("admin"))
):
    await connect_db()
    affected = await execute_query(
        "UPDATE users SET balance = %s WHERE id = %s",
        (user_balance, user_id),
        return_rowcount=True
    )
    await close_db()

    if affected == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return {"message": f"User balance set to {user_balance} IRR"}

@router.get("/{user_id}/roles", response_model=List[dict])
async def get_user_roles(
    user_id: int,
    current_user: dict = Depends(get_current_user)
):
    if current_user["user_id"] != user_id and not await has_permission(current_user["user_id"], "read:user_roles") and not is_admin(current_user["user_id"]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view these roles"
        )
    
    await connect_db()
    roles = await execute_query(
        """
        SELECT r.id, r.name, r.description, ur.assigned_at, ur.expired_at
        FROM user_role ur
        JOIN roles r ON ur.role_id = r.id
        WHERE ur.user_id = %s AND (ur.expired_at IS NULL OR ur.expired_at > NOW())
        """,
        (user_id,),
        fetch_all=True
    )
    await close_db()
    return roles

@router.get("/{user_id}/permissions", response_model=List[dict])
async def get_user_permissions(
    user_id: int,
    current_user: dict = Depends(get_current_user)
):
    if current_user["user_id"] != user_id and not await has_permission(current_user["user_id"], "read:user_permissions") and not is_admin(current_user["user_id"]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view these permissions"
        )
    await connect_db()
    permissions = await execute_query(
        """
        SELECT 
            p.id AS permission_id,
            p.name AS permission_name,
            p.description AS permission_description,
            r.id AS role_id,
            r.name AS role_name,
            r.description AS role_description
        FROM user_role ur
        JOIN roles r ON ur.role_id = r.id
        JOIN role_permissions rp ON r.id = rp.role_id
        JOIN permissions p ON rp.permission_id = p.id
        WHERE ur.user_id = %s
          AND (ur.expired_at IS NULL OR ur.expired_at > NOW())
        """,
        (user_id,),
        fetch_all=True
    )
    await close_db()
    
    return permissions


@router.get("/{user_id}/balance", response_model=int)
async def get_user_balance(
        user_id: int,
        current_user: dict = Depends(get_current_user)
):
    if current_user["user_id"] != user_id and not is_admin(
            current_user["user_id"]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view user balance"
        )
    await connect_db()
    user = await execute_query(
        """
        SELECT balance
        FROM users
        WHERE id = %s
        """,
        (user_id,),
        fetch_one=True
    )
    await close_db()

    return user["balance"]