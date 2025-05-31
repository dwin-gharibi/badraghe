from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from app.db import execute_query, close_db, connect_db
from app.utils.auth_util import get_current_user, require_roles
from app.utils.rbac_util import has_permission
from app.config import settings

router = APIRouter(prefix="/users")

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
    if current_user["user_id"] != user_id and not await has_permission(current_user["user_id"], "read:users"):
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
               status, is_verified, bio, preferences,
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
    update_data: dict,
    current_user: dict = Depends(get_current_user)
):
    if current_user["user_id"] != user_id and not await has_permission(current_user["user_id"], "update:users"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this user"
        )

    await connect_db()
    allowed_fields = {
        "first_name", "last_name", "country", "state", "city",
        "address", "zip_code", "date_of_birth", "gender", "bio"
    }
    
    if not await has_permission(current_user["user_id"], "update:users"):
        update_data = {k: v for k, v in update_data.items() if k in allowed_fields}

    set_clause = ", ".join([f"{field} = %s" for field in update_data.keys()])
    values = list(update_data.values())
    values.append(user_id)

    try:
        await execute_query(
            f"UPDATE users SET {set_clause} WHERE id = %s",
            values,
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
            "UPDATE users SET status = 0 WHERE id = %s AND status = 1",
            (user_id,),
            return_rowcount=True
        )
        if affected == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found or already inactive"
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

@router.get("/{user_id}/roles", response_model=List[dict])
async def get_user_roles(
    user_id: int,
    current_user: dict = Depends(get_current_user)
):
    if current_user["user_id"] != user_id and not await has_permission(current_user["user_id"], "read:user_roles"):
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
    if current_user["user_id"] != user_id and not await has_permission(current_user["user_id"], "read:user_permissions"):
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
