from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional, Dict
from datetime import datetime
from pydantic import BaseModel
from enum import Enum
from app.db import execute_query, connect_db, close_db
from app.utils.auth_util import get_current_user, require_roles
from app.utils.rbac_util import has_permission

router = APIRouter(prefix="/support")

class TicketPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class TicketStatus(str, Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"

class MessageType(str, Enum):
    USER = "user"
    BOT = "bot"
    SUPPORT = "support"

class SupportCategoryCreate(BaseModel):
    name: str
    description: Optional[str] = None

class SupportCategoryResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    created_at: datetime
    updated_at: datetime

class SupportTicketCreate(BaseModel):
    category_id: int
    subject: str
    description: str
    priority: TicketPriority = TicketPriority.LOW

class SupportTicketUpdate(BaseModel):
    category_id: Optional[int] = None
    subject: Optional[str] = None
    priority: Optional[TicketPriority] = None
    assigned_to: Optional[int] = None
    status: Optional[TicketStatus] = None

class SupportTicketResponse(BaseModel):
    id: int
    user_id: int
    category_id: int
    subject: str
    description: str
    status: TicketStatus
    priority: TicketPriority
    assigned_to: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    category_name: Optional[str] = None
    user_email: Optional[str] = None
    assigned_email: Optional[str] = None

class SupportMessageCreate(BaseModel):
    message: str
    message_type: MessageType = MessageType.USER

class SupportMessageResponse(BaseModel):
    id: int
    ticket_id: int
    user_id: int
    message: str
    message_type: MessageType
    created_at: datetime
    user_email: Optional[str] = None

class TicketStatsResponse(BaseModel):
    total_tickets: int
    open: int
    in_progress: int
    resolved: int
    closed: int
    by_category: Dict[str, int]
    by_priority: Dict[str, int]

@router.get("/categories", response_model=List[SupportCategoryResponse])
async def get_support_categories(
    include_inactive: bool = False
):
    await connect_db()
    query = "SELECT * FROM support_categories"
    params = []
    
    if not include_inactive:
        query += " WHERE status = TRUE"
    
    query += " ORDER BY name"
    
    categories = await execute_query(query, params, fetch_all=True)
    await close_db()
    return categories

@router.post("/categories", status_code=status.HTTP_201_CREATED, response_model=SupportCategoryResponse)
async def create_support_category(
    category: SupportCategoryCreate,
    current_user: dict = Depends(require_roles("admin"))
):
    await connect_db()
    existing = await execute_query(
        "SELECT 1 FROM support_categories WHERE name = %s",
        (category.name,),
        fetch_one=True
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Category with this name already exists"
        )

    try:
        category_data = await execute_query(
            """
            INSERT INTO support_categories (name, description)
            VALUES (%s, %s)
            RETURNING *
            """,
            (category.name, category.description),
            fetch_one=True
        )
        await close_db()
        return category_data
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.put("/categories/{category_id}", response_model=SupportCategoryResponse)
async def update_support_category(
    category_id: int,
    category: SupportCategoryCreate,
    current_user: dict = Depends(require_roles("admin"))
):
    await connect_db()
    existing = await execute_query(
        "SELECT 1 FROM support_categories WHERE id = %s",
        (category_id,),
        fetch_one=True
    )
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )

    conflict = await execute_query(
        "SELECT 1 FROM support_categories WHERE name = %s AND id != %s",
        (category.name, category_id),
        fetch_one=True
    )
    if conflict:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Category with this name already exists"
        )

    try:
        updated = await execute_query(
            """
            UPDATE support_categories
            SET name = %s, description = %s
            WHERE id = %s
            RETURNING *
            """,
            (category.name, category.description, category_id),
            fetch_one=True
        )
        await close_db()
        return updated
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

async def get_ticket_with_details(ticket_id: int) -> Optional[dict]:
    await connect_db()
    ticket = await execute_query(
        """
        SELECT t.*, c.name as category_name, 
               u.email as user_email, a.email as assigned_email
        FROM support_tickets t
        JOIN support_categories c ON t.category_id = c.id
        JOIN users u ON t.user_id = u.id
        LEFT JOIN users a ON t.assigned_to = a.id
        WHERE t.id = %s
        """,
        (ticket_id,),
        fetch_one=True
    )
    
    if ticket:
        conversation = await execute_query(
            """
            SELECT c.*, u.email as user_email
            FROM support_ticket_conversations c
            LEFT JOIN users u ON c.user_id = u.id
            WHERE c.ticket_id = %s
            ORDER BY c.created_at ASC
            """,
            (ticket_id,),
            fetch_all=True
        )
        ticket["conversation"] = conversation
    
    await close_db()
    return ticket