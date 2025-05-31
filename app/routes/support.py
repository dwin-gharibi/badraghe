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
            """,
            (category.name, category.description),
            fetch_one=True,
            return_lastrowid=True
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
            """,
            (category.name, category.description, category_id),
            fetch_one=True,
            return_lastrowid=True
        )
        await close_db()
        return updated
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/tickets", status_code=status.HTTP_201_CREATED, response_model=SupportTicketResponse)
async def create_support_ticket(
    ticket: SupportTicketCreate,
    current_user: dict = Depends(get_current_user)
):
    await connect_db()
    category = await execute_query(
        "SELECT 1 FROM support_categories WHERE id = %s",
        (ticket.category_id,),
        fetch_one=True
    )
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )

    try:
        ticket_data = await execute_query(
            """
            INSERT INTO support_tickets (
                user_id, category_id, subject,
                description, status, priority
            ) VALUES (%s, %s, %s, %s, 'open', %s)
            """,
            (
                current_user["user_id"],
                ticket.category_id,
                ticket.subject,
                ticket.description,
                ticket.priority.value
            ),
            fetch_one=True,
            return_lastrowid=True
        )
        
        await execute_query(
            """
            INSERT INTO support_ticket_conversations (
                ticket_id, user_id, message, message_type
            ) VALUES (%s, %s, %s, 'user')
            """,
            (
                ticket_data["id"],
                current_user["user_id"],
                ticket.description
            ),
            commit=True
        )
        
        await close_db()
        return await get_ticket_with_details(ticket_data["id"])
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/tickets", response_model=List[SupportTicketResponse])
async def get_support_tickets(
    status: Optional[TicketStatus] = None,
    category_id: Optional[int] = None,
    priority: Optional[TicketPriority] = None,
    assigned_to_me: bool = False,
    user_id: Optional[int] = None,
    search: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    skip: int = 0,
    limit: int = 100,
    current_user: dict = Depends(get_current_user)
):
    await connect_db()
    query = """
    SELECT t.*, c.name as category_name, 
           u.email as user_email, a.email as assigned_email
    FROM support_tickets t
    JOIN support_categories c ON t.category_id = c.id
    JOIN users u ON t.user_id = u.id
    LEFT JOIN users a ON t.assigned_to = a.id
    WHERE 1=1
    """
    params = []
    
    if status:
        query += " AND t.status = %s"
        params.append(status.value)
    
    if category_id:
        query += " AND t.category_id = %s"
        params.append(category_id)
    
    if priority:
        query += " AND t.priority = %s"
        params.append(priority.value)
    
    if user_id:
        query += " AND t.user_id = %s"
        params.append(user_id)
    
    if search:
        query += " AND (t.subject ILIKE %s OR t.description ILIKE %s)"
        params.extend([f"%{search}%", f"%{search}%"])
    
    if start_date:
        query += " AND t.created_at >= %s"
        params.append(start_date)
    
    if end_date:
        query += " AND t.created_at <= %s"
        params.append(end_date)
    
    if not await has_permission(current_user["user_id"], "view_all:tickets"):
        query += " AND t.user_id = %s"
        params.append(current_user["user_id"])
    elif assigned_to_me:
        query += " AND t.assigned_to = %s"
        params.append(current_user["user_id"])
    
    query += " ORDER BY t.created_at DESC LIMIT %s OFFSET %s"
    params.extend([limit, skip])
    
    tickets = await execute_query(query, params, fetch_all=True)
    await close_db()
    return tickets

@router.get("/tickets/{ticket_id}", response_model=SupportTicketResponse)
async def get_support_ticket(
    ticket_id: int,
    current_user: dict = Depends(get_current_user)
):
    await connect_db()
    ticket = await get_ticket_with_details(ticket_id)
    
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found"
        )
    
    if (ticket["user_id"] != current_user["user_id"] and 
        not await has_permission(current_user["user_id"], "view_all:tickets")):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this ticket"
        )
    
    await close_db()
    return ticket

@router.put("/tickets/{ticket_id}", response_model=SupportTicketResponse)
async def update_support_ticket(
    ticket_id: int,
    update: SupportTicketUpdate,
    current_user: dict = Depends(get_current_user)
):
    await connect_db()
    ticket = await execute_query(
        "SELECT * FROM support_tickets WHERE id = %s",
        (ticket_id,),
        fetch_one=True
    )
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found"
        )
    
    if (ticket["user_id"] != current_user["user_id"] and 
        not await has_permission(current_user["user_id"], "manage:tickets")):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this ticket"
        )
    
    set_clause = []
    params = []
    
    if update.category_id:
        category = await execute_query(
            "SELECT 1 FROM support_categories WHERE id = %s",
            (update.category_id,),
            fetch_one=True
        )
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found"
            )
        set_clause.append("category_id = %s")
        params.append(update.category_id)
    
    if update.subject:
        set_clause.append("subject = %s")
        params.append(update.subject)
    
    if update.priority:
        set_clause.append("priority = %s")
        params.append(update.priority.value)
    
    if update.assigned_to is not None:
        if update.assigned_to:
            user = await execute_query(
                """
                SELECT 1 FROM user_role ur 
                JOIN roles r ON ur.role_id = r.id 
                WHERE ur.user_id = %s AND r.name IN ('admin', 'support_agent')
                """,
                (update.assigned_to,),
                fetch_one=True
            )
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Assigned user must be admin or support agent"
                )
        set_clause.append("assigned_to = %s")
        params.append(update.assigned_to)
    
    if update.status:
        set_clause.append("status = %s")
        params.append(update.status.value)
    
    if not set_clause:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields to update"
        )
    
    params.append(ticket_id)
    
    try:
        await execute_query(
            f"UPDATE support_tickets SET {', '.join(set_clause)} WHERE id = %s",
            params,
            commit=True
        )
        await close_db()
        return await get_ticket_with_details(ticket_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.delete("/tickets/{ticket_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_support_ticket(
    ticket_id: int,
    current_user: dict = Depends(require_roles("admin"))
):
    await connect_db()
    ticket = await execute_query(
        "SELECT 1 FROM support_tickets WHERE id = %s",
        (ticket_id,),
        fetch_one=True
    )
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found"
        )
    
    try:
        await execute_query(
            "DELETE FROM support_ticket_conversations WHERE ticket_id = %s",
            (ticket_id,),
            commit=True
        )
        
        await execute_query(
            "DELETE FROM support_tickets WHERE id = %s",
            (ticket_id,),
            commit=True
        )
        await close_db()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/tickets/{ticket_id}/messages", status_code=status.HTTP_201_CREATED, response_model=SupportMessageResponse)
async def add_ticket_message(
    ticket_id: int,
    message: SupportMessageCreate,
    current_user: dict = Depends(get_current_user)
):
    await connect_db()
    ticket = await execute_query(
        "SELECT user_id, status FROM support_tickets WHERE id = %s",
        (ticket_id,),
        fetch_one=True
    )
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found"
        )
    
    if (ticket["user_id"] != current_user["user_id"] and 
        not await has_permission(current_user["user_id"], "respond:tickets")):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to add messages to this ticket"
        )
    
    try:
        message_data = await execute_query(
            """
            INSERT INTO support_ticket_conversations (
                ticket_id, user_id, message, message_type
            ) VALUES (%s, %s, %s, %s)
            """,
            (
                ticket_id,
                current_user["user_id"],
                message.message,
                message.message_type.value
            ),
            fetch_one=True,
            return_lastrowid=True
        )
        
        if ticket["status"] == "closed":
            await execute_query(
                "UPDATE support_tickets SET status = 'open' WHERE id = %s",
                (ticket_id,),
                commit=True
            )
        
        user = await execute_query(
            "SELECT email FROM users WHERE id = %s",
            (current_user["user_id"],),
            fetch_one=True
        )
        await close_db()
        return {**message_data, "user_email": user["email"] if user else None}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/tickets/{ticket_id}/messages", response_model=List[SupportMessageResponse])
async def get_ticket_messages(
    ticket_id: int,
    skip: int = 0,
    limit: int = 100,
    current_user: dict = Depends(get_current_user)
):
    await connect_db()
    ticket = await execute_query(
        "SELECT user_id FROM support_tickets WHERE id = %s",
        (ticket_id,),
        fetch_one=True
    )
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found"
        )
    
    if (ticket["user_id"] != current_user["user_id"] and 
        not await has_permission(current_user["user_id"], "view_all:tickets")):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view messages for this ticket"
        )
    
    messages = await execute_query(
        """
        SELECT c.*, u.email as user_email
        FROM support_ticket_conversations c
        LEFT JOIN users u ON c.user_id = u.id
        WHERE c.ticket_id = %s
        ORDER BY c.created_at ASC
        LIMIT %s OFFSET %s
        """,
        (ticket_id, limit, skip),
        fetch_all=True
    )
    await close_db()
    return messages

@router.get("/stats", response_model=TicketStatsResponse)
async def get_support_stats(
    time_range: Optional[str] = Query(None, description="Time range: today, week, month, year"),
    current_user: dict = Depends(require_roles("admin", "support_agent"))
):
    await connect_db()
    time_conditions = {
        "today": "DATE(created_at) = CURRENT_DATE",
        "week": "created_at >= DATE_SUB(CURRENT_DATE, INTERVAL 7 DAY)",
        "month": "created_at >= DATE_SUB(CURRENT_DATE, INTERVAL 1 MONTH)",
        "year": "created_at >= DATE_SUB(CURRENT_DATE, INTERVAL 1 YEAR)"
    }
    
    where_clause = f" WHERE {time_conditions[time_range]}" if time_range else ""
    
    status_counts = await execute_query(
        f"SELECT status, COUNT(*) as count FROM support_tickets{where_clause} GROUP BY status",
        fetch_all=True
    )
    
    category_counts = await execute_query(
        f"""
        SELECT c.name, COUNT(*) as count 
        FROM support_tickets t
        JOIN support_categories c ON t.category_id = c.id
        {where_clause}
        GROUP BY c.name
        """,
        fetch_all=True
    )
    
    priority_counts = await execute_query(
        f"SELECT priority, COUNT(*) as count FROM support_tickets{where_clause} GROUP BY priority",
        fetch_all=True
    )
    
    stats = {
        "total_tickets": 0,
        "open": 0,
        "in_progress": 0,
        "resolved": 0,
        "closed": 0,
        "by_category": {},
        "by_priority": {}
    }
    
    for row in status_counts:
        stats["total_tickets"] += row["count"]
        stats[row["status"]] = row["count"]
    
    for row in category_counts:
        stats["by_category"][row["name"]] = row["count"]
    
    for row in priority_counts:
        stats["by_priority"][row["priority"]] = row["count"]
    
    await close_db()
    return stats

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