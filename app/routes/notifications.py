from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional, Dict
from datetime import datetime
from pydantic import BaseModel
from enum import Enum
from app.db import execute_query, connect_db, close_db
from app.utils.auth_util import get_current_user, require_roles
from app.utils.rbac_util import has_permission

router = APIRouter(prefix="/notifications")

class NotificationStatus(str, Enum):
    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"

class NotificationType(str, Enum):
    SYSTEM = "system"
    USER = "user"
    TRANSACTION = "transaction"
    OTHER = "other"

class NotificationCreate(BaseModel):
    user_id: int
    message: str
    notification_type: NotificationType = NotificationType.SYSTEM
    metadata: Optional[dict] = None

class NotificationUpdate(BaseModel):
    message: Optional[str] = None
    status: Optional[NotificationStatus] = None
    notification_type: Optional[NotificationType] = None
    is_read: Optional[bool] = None
    metadata: Optional[dict] = None

class NotificationResponse(BaseModel):
    id: int
    user_id: int
    message: str
    status: NotificationStatus
    notification_type: NotificationType
    is_read: bool
    sent_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    metadata: Optional[dict] = None
    user_email: Optional[str] = None

class NotificationStatsResponse(BaseModel):
    total_notifications: int
    unread: int
    sent: int
    failed: int
    by_type: Dict[str, int]

@router.get("/", response_model=List[NotificationResponse])
async def get_user_notifications(
    unread_only: bool = False,
    status_filter: Optional[NotificationStatus] = None,
    type_filter: Optional[NotificationType] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    skip: int = 0,
    limit: int = 100,
    current_user: dict = Depends(get_current_user)
):
    await connect_db()
    query = """
    SELECT n.*, u.email as user_email
    FROM notifications n
    JOIN users u ON n.user_id = u.id
    WHERE n.user_id = %s
    """
    params = [current_user["user_id"]]
    
    if unread_only:
        query += " AND n.is_read = FALSE"
    
    if status_filter:
        query += " AND n.status = %s"
        params.append(status_filter.value)
    
    if type_filter:
        query += " AND n.notification_type = %s"
        params.append(type_filter.value)
    
    if start_date:
        query += " AND n.created_at >= %s"
        params.append(start_date)
    
    if end_date:
        query += " AND n.created_at <= %s"
        params.append(end_date)
    
    query += " ORDER BY n.created_at DESC LIMIT %s OFFSET %s"
    params.extend([limit, skip])
    
    notifications = await execute_query(query, params, fetch_all=True)
    await close_db()
    return notifications

@router.get("/all", response_model=List[NotificationResponse])
async def get_all_notifications(
    user_id: Optional[int] = None,
    status_filter: Optional[NotificationStatus] = None,
    type_filter: Optional[NotificationType] = None,
    is_read: Optional[bool] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    skip: int = 0,
    limit: int = 100,
    current_user: dict = Depends(require_roles("admin"))
):
    await connect_db()

    query = """
    SELECT n.*, u.email as user_email
    FROM notifications n
    JOIN users u ON n.user_id = u.id
    WHERE 1=1
    """
    params = []
    
    if user_id:
        query += " AND n.user_id = %s"
        params.append(user_id)
    
    if status_filter:
        query += " AND n.status = %s"
        params.append(status_filter.value)
    
    if type_filter:
        query += " AND n.notification_type = %s"
        params.append(type_filter.value)
    
    if is_read is not None:
        query += " AND n.is_read = %s"
        params.append(is_read)
    
    if start_date:
        query += " AND n.created_at >= %s"
        params.append(start_date)
    
    if end_date:
        query += " AND n.created_at <= %s"
        params.append(end_date)
    
    query += " ORDER BY n.created_at DESC LIMIT %s OFFSET %s"
    params.extend([limit, skip])
    
    notifications = await execute_query(query, params, fetch_all=True)
    await connect_db()
    return notifications

@router.get("/{notification_id}", response_model=NotificationResponse)
async def get_notification_details(
    notification_id: int,
    current_user: dict = Depends(get_current_user)
):
    await connect_db()
    notification = await execute_query(
        """
        SELECT n.*, u.email as user_email
        FROM notifications n
        JOIN users u ON n.user_id = u.id
        WHERE n.id = %s
        """,
        (notification_id,),
        fetch_one=True
    )
    
    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )
    
    if (notification["user_id"] != current_user["user_id"] and 
        not await has_permission(current_user["user_id"], "view_all:notifications")):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this notification"
        )

    await close_db()
    
    return notification

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=NotificationResponse)
async def create_notification(
    notification: NotificationCreate,
    current_user: dict = Depends(require_roles("admin", "support_agent"))
):
    await connect_db()

    user = await execute_query(
        "SELECT 1 FROM users WHERE id = %s",
        (notification.user_id,),
        fetch_one=True
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    try:
        notification_data = await execute_query(
            """
            INSERT INTO notifications (
                user_id, message, status,
                notification_type, metadata
            ) VALUES (%s, %s, 'pending', %s, %s)
            RETURNING *
            """,
            (
                notification.user_id,
                notification.message,
                notification.notification_type.value,
                notification.metadata or {}
            ),
            fetch_one=True
        )
        
        await close_db()
        
        return await get_notification_details(notification_data["id"])
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/batch", status_code=status.HTTP_201_CREATED)
async def create_batch_notifications(
    user_ids: List[int],
    message: str,
    notification_type: NotificationType = NotificationType.SYSTEM,
    metadata: Optional[dict] = None,
    current_user: dict = Depends(require_roles("admin"))
):
    await connect_db()
    if not user_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one user_id must be provided"
        )
    
    existing_users = await execute_query(
        f"SELECT id FROM users WHERE id IN ({','.join(['%s']*len(user_ids))})",
        user_ids,
        fetch_all=True
    )
    if len(existing_users) != len(user_ids):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="One or more users not found"
        )
    
    try:
        for user_id in user_ids:
            await execute_query(
                """
                INSERT INTO notifications (
                    user_id, message, status,
                    notification_type, metadata
                ) VALUES (%s, %s, 'pending', %s, %s)
                """,
                (
                    user_id,
                    message,
                    notification_type.value,
                    metadata or {}
                ),
                commit=True
            )
        
        await close_db()
        return {"message": f"Notifications created for {len(user_ids)} users"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.put("/{notification_id}", response_model=NotificationResponse)
async def update_notification(
    notification_id: int,
    update: NotificationUpdate,
    current_user: dict = Depends(require_roles("admin"))
):
    await connect_db()
    notification = await execute_query(
        "SELECT * FROM notifications WHERE id = %s",
        (notification_id,),
        fetch_one=True
    )
    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )
    
    set_clause = []
    params = []
    
    if update.message:
        set_clause.append("message = %s")
        params.append(update.message)
    
    if update.status:
        set_clause.append("status = %s")
        params.append(update.status.value)
    
    if update.notification_type:
        set_clause.append("notification_type = %s")
        params.append(update.notification_type.value)
    
    if update.is_read is not None:
        set_clause.append("is_read = %s")
        params.append(update.is_read)
    
    if update.metadata is not None:
        set_clause.append("metadata = %s")
        params.append(update.metadata or {})
    
    if not set_clause:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields to update"
        )
    
    params.append(notification_id)
    
    try:
        await execute_query(
            f"UPDATE notifications SET {', '.join(set_clause)} WHERE id = %s",
            params,
            commit=True
        )
        await close_db()
        return await get_notification_details(notification_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
