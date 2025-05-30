from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
from app.db import execute_query, connect_db, close_db
from app.utils.auth_util import get_current_user, require_roles

router = APIRouter(prefix="/roles")

class RoleCreate(BaseModel):
    name: str
    description: Optional[str] = None
    parent_role_id: Optional[int] = None
    status: bool = True

class RoleUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    parent_role_id: Optional[int] = None
    status: Optional[bool] = None

class PermissionCreate(BaseModel):
    name: str
    description: Optional[str] = None
    type: str
    status: bool = True

async def _get_role(role_id: int):
    role = await execute_query(
        """
        SELECT r.*, p.name as parent_name
        FROM roles r
        LEFT JOIN roles p ON r.parent_role_id = p.id
        WHERE r.id = %s
        """,
        (role_id,),
        fetch_one=True
    )
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found"
        )
    return role

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_role(
    role: RoleCreate,
    current_user: dict = Depends(require_roles("admin"))
):
    await connect_db()
    existing = await execute_query(
        "SELECT 1 FROM roles WHERE name = %s",
        (role.name,),
        fetch_one=True
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Role with this name already exists"
        )

    if role.parent_role_id:
        parent = await execute_query(
            "SELECT 1 FROM roles WHERE id = %s",
            (role.parent_role_id,),
            fetch_one=True
        )
        if not parent:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Parent role not found"
            )

    try:
        role_id = await execute_query(
            """
            INSERT INTO roles (
                name, description, parent_role_id, status
            ) VALUES (%s, %s, %s, %s)
            RETURNING id
            """,
            (
                role.name, role.description,
                role.parent_role_id, role.status
            ),
            fetch_one=True
        )
        await close_db()
        return {"role_id": role_id["id"]}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/", response_model=List[dict])
async def get_all_roles(
    active_only: bool = False,
    skip: int = 0,
    limit: int = 100,
    current_user: dict = Depends(require_roles("admin"))
):
    await connect_db()
    query = """
    SELECT r.*, p.name as parent_name
    FROM roles r
    LEFT JOIN roles p ON r.parent_role_id = p.id
    WHERE 1=1
    """
    params = []
    
    if active_only:
        query += " AND r.status = TRUE"
    
    query += " ORDER BY r.name ASC LIMIT %s OFFSET %s"
    params.extend([limit, skip])
    
    roles = await execute_query(query, params, fetch_all=True)
    await close_db()
    return roles

@router.get("/{role_id}", response_model=dict)
async def get_role(
    role_id: int,
    current_user: dict = Depends(require_roles("admin"))
):
    return await _get_role(role_id)

@router.put("/{role_id}", response_model=dict)
async def update_role(
    role_id: int,
    role: RoleCreate,
    current_user: dict = Depends(require_roles("admin"))
):
    await connect_db()
    existing = await execute_query(
        "SELECT 1 FROM roles WHERE name = %s AND id != %s",
        (role.name, role_id),
        fetch_one=True
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Role with this name already exists"
        )

    if role.parent_role_id:
        if role.parent_role_id == role_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Role cannot be its own parent"
            )
        parent = await execute_query(
            "SELECT 1 FROM roles WHERE id = %s",
            (role.parent_role_id,),
            fetch_one=True
        )
        if not parent:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Parent role not found"
            )

    try:
        await execute_query(
            """
            UPDATE roles 
            SET name = %s, description = %s,
                parent_role_id = %s, status = %s
            WHERE id = %s
            """,
            (
                role.name, role.description,
                role.parent_role_id, role.status, role_id
            ),
            commit=True
        )
        await close_db()
        return await _get_role(role_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.patch("/{role_id}", response_model=dict)
async def partial_update_role(
    role_id: int,
    role: RoleUpdate,
    current_user: dict = Depends(require_roles("admin"))
):
    await connect_db()
    update_data = role.dict(exclude_unset=True)
    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields to update"
        )

    if "name" in update_data:
        existing = await execute_query(
            "SELECT 1 FROM roles WHERE name = %s AND id != %s",
            (update_data["name"], role_id),
            fetch_one=True
        )
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Role with this name already exists"
            )

    if "parent_role_id" in update_data:
        if update_data["parent_role_id"] == role_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Role cannot be its own parent"
            )
        if update_data["parent_role_id"]:
            parent = await execute_query(
                "SELECT 1 FROM roles WHERE id = %s",
                (update_data["parent_role_id"],),
                fetch_one=True
            )
            if not parent:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Parent role not found"
                )

    set_clause = ", ".join([f"{field} = %s" for field in update_data.keys()])
    values = list(update_data.values())
    values.append(role_id)

    try:
        await execute_query(
            f"UPDATE roles SET {set_clause} WHERE id = %s",
            values,
            commit=True
        )
        await close_db()
        return await _get_role(role_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
