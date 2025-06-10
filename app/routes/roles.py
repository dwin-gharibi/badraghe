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


@router.post("/permissions", status_code=status.HTTP_201_CREATED)
async def create_permission(
        permission: PermissionCreate,
        current_user: dict = Depends(require_roles("admin"))
):
    await connect_db()
    valid_types = ["create", "read", "update", "delete"]
    if permission.type not in valid_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid permission type. Must be one of: {', '.join(valid_types)}"
        )

    existing = await execute_query(
        "SELECT 1 FROM permissions WHERE name = %s",
        (permission.name,),
        fetch_one=True
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Permission with this name already exists"
        )

    try:
        perm_id = await execute_query(
            """
            INSERT INTO permissions (
                name, description, type, status
            ) VALUES (%s, %s, %s, %s)
            """,
            (
                permission.name, permission.description,
                permission.type, permission.status
            ),
            fetch_one=True,
            return_lastrowid=True
        )
        await close_db()
        return {"permission_id": perm_id}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/permissions", response_model=List[dict])
async def get_all_permissions(
        type_filter: Optional[str] = None,
        status_filter: Optional[bool] = None,
        skip: int = 0,
        limit: int = 100,
        current_user: dict = Depends(require_roles("admin"))
):
    await connect_db()
    query = "SELECT * FROM permissions WHERE 1=1"
    params = []

    if type_filter:
        query += " AND type = %s"
        params.append(type_filter)

    if status_filter is not None:
        query += " AND status = %s"
        params.append(status_filter)

    query += " ORDER BY name ASC LIMIT %s OFFSET %s"
    params.extend([limit, skip])

    permissions = await execute_query(query, params, fetch_all=True)
    await close_db()

    return permissions

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
            """,
            (
                role.name, role.description,
                role.parent_role_id, role.status
            ),
            fetch_one=True,
            return_lastrowid=True
        )
        await close_db()
        return {"role_id": role_id}
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
        return await _get_role(role_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.delete("/{role_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_role(
    role_id: int,
    current_user: dict = Depends(require_roles("admin"))
):
    await connect_db()
    users = await execute_query(
        "SELECT 1 FROM user_role WHERE role_id = %s LIMIT 1",
        (role_id,),
        fetch_one=True
    )
    if users:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete role assigned to users"
        )

    perms = await execute_query(
        "SELECT 1 FROM role_permissions WHERE role_id = %s LIMIT 1",
        (role_id,),
        fetch_one=True
    )
    if perms:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete role with assigned permissions"
        )

    children = await execute_query(
        "SELECT 1 FROM roles WHERE parent_role_id = %s LIMIT 1",
        (role_id,),
        fetch_one=True
    )
    if children:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete role that is parent of other roles"
        )

    affected = await execute_query(
        "DELETE FROM roles WHERE id = %s",
        (role_id,),
        commit=True
    )
    await close_db()
    if not affected:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found"
        )

@router.get("/{role_id}/permissions", response_model=List[dict])
async def get_role_permissions(
    role_id: int,
    current_user: dict = Depends(require_roles("admin"))
):
    await connect_db()
    permissions = await execute_query(
        """
        SELECT p.id, p.name, p.description, p.type, p.status
        FROM role_permissions rp
        JOIN permissions p ON rp.permission_id = p.id
        WHERE rp.role_id = %s
        """,
        (role_id,),
        fetch_all=True
    )
    await close_db()
    return permissions

@router.post("/{role_id}/permissions/{permission_id}", status_code=status.HTTP_201_CREATED)
async def assign_permission_to_role(
    role_id: int,
    permission_id: int,
    current_user: dict = Depends(require_roles("admin"))
):
    await connect_db()
    role = await execute_query(
        "SELECT 1 FROM roles WHERE id = %s",
        (role_id,),
        fetch_one=True
    )
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found"
        )

    permission = await execute_query(
        "SELECT 1 FROM permissions WHERE id = %s",
        (permission_id,),
        fetch_one=True
    )
    if not permission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Permission not found"
        )

    try:
        await execute_query(
            "INSERT IGNORE INTO role_permissions (role_id, permission_id) VALUES (%s, %s)",
            (role_id, permission_id),
            commit=True
        )
        await close_db()
        return {"message": "Permission assigned to role successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.delete("/{role_id}/permissions/{permission_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_permission_from_role(
    role_id: int,
    permission_id: int,
    current_user: dict = Depends(require_roles("admin"))
):
    await connect_db()
    affected = await execute_query(
        "DELETE FROM role_permissions WHERE role_id = %s AND permission_id = %s",
        (role_id, permission_id),
        commit=True
    )
    await close_db()
    if not affected:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Permission assignment not found"
        )

@router.patch("/permissions/{permission_id}", response_model=dict)
async def update_permission(
    permission_id: int,
    permission: PermissionCreate,
    current_user: dict = Depends(require_roles("admin"))
):
    await connect_db()
    valid_types = ["create", "read", "update", "delete"]
    if permission.type not in valid_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid permission type. Must be one of: {', '.join(valid_types)}"
        )

    existing = await execute_query(
        "SELECT 1 FROM permissions WHERE name = %s AND id != %s",
        (permission.name, permission_id),
        fetch_one=True
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Permission with this name already exists"
        )

    try:
        await execute_query(
            """
            UPDATE permissions 
            SET name = %s, description = %s,
                type = %s, status = %s
            WHERE id = %s
            """,
            (
                permission.name, permission.description,
                permission.type, permission.status, permission_id
            ),
            commit=True
        )
        return await execute_query(
            "SELECT * FROM permissions WHERE id = %s",
            (permission_id,),
            fetch_one=True
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.delete("/permissions/{permission_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_permission(
    permission_id: int,
    current_user: dict = Depends(require_roles("admin"))
):
    await connect_db()
    roles = await execute_query(
        "SELECT 1 FROM role_permissions WHERE permission_id = %s LIMIT 1",
        (permission_id,),
        fetch_one=True
    )
    if roles:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete permission assigned to roles"
        )

    affected = await execute_query(
        "DELETE FROM permissions WHERE id = %s",
        (permission_id,),
        commit=True
    )
    await close_db()
    if not affected:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Permission not found"
        )