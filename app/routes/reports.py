from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional, Dict
from datetime import datetime
from pydantic import BaseModel
from app.db import execute_query, connect_db, close_db
from app.utils.auth_util import get_current_user, require_roles
from app.utils.rbac_util import get_user_roles, has_permission

router = APIRouter(prefix="/reports")

class ReportCreate(BaseModel):
    ticket_id: Optional[int] = None
    category: str
    message: str

class ReportUpdate(BaseModel):
    status: Optional[str] = None
    resolution: Optional[str] = None
    assigned_to: Optional[int] = None

class ReportResponse(BaseModel):
    id: int
    user_id: int
    ticket_id: Optional[int]
    category: str
    message: str
    status: str
    resolution: Optional[str]
    assigned_to: Optional[int]
    created_at: datetime
    updated_at: datetime

class ReportStatsResponse(BaseModel):
    total_reports: int
    pending: int
    reviewed: int
    resolved: int
    by_category: Dict[str, int]

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=ReportResponse)
async def create_report(
    report: ReportCreate,
    current_user: dict = Depends(get_current_user)
):
    await connect_db()
    valid_categories = ["payment_issue", "delay", "cancellation", "other"]
    if report.category not in valid_categories:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid category. Must be one of: {', '.join(valid_categories)}"
        )

    if report.ticket_id:
        ticket = await execute_query(
            "SELECT 1 FROM travel_tickets WHERE id = %s",
            (report.ticket_id,),
            fetch_one=True
        )
        if not ticket:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ticket not found"
            )

    try:
        report_data = await execute_query(
            """
            INSERT INTO reports (
                user_id, ticket_id, category, message, status
            ) VALUES (%s, %s, %s, %s, 'pending')
            RETURNING *
            """,
            (current_user["user_id"], report.ticket_id, report.category, report.message),
            fetch_one=True
        )
        await close_db()
        return report_data
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/", response_model=List[ReportResponse])
async def get_user_reports(
    status_filter: Optional[str] = None,
    category: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    current_user: dict = Depends(get_current_user)
):
    await connect_db()
    query = """
    SELECT r.*, t.id as ticket_id
    FROM reports r
    LEFT JOIN travel_tickets t ON r.ticket_id = t.id
    WHERE r.user_id = %s
    """
    params = [current_user["user_id"]]
    
    if status_filter:
        query += " AND r.status = %s"
        params.append(status_filter)
    
    if category:
        query += " AND r.category = %s"
        params.append(category)
    
    if start_date:
        query += " AND r.created_at >= %s"
        params.append(start_date)
    
    if end_date:
        query += " AND r.created_at <= %s"
        params.append(end_date)
    
    query += " ORDER BY r.created_at DESC"
    
    reports = await execute_query(query, params, fetch_all=True)
    await close_db()
    return reports

@router.get("/{report_id}", response_model=ReportResponse)
async def get_report_details(
    report_id: int,
    current_user: dict = Depends(get_current_user)
):
    await connect_db()
    report = await execute_query(
        """
        SELECT r.*, t.id as ticket_id, 
               u.email as user_email, u.first_name as user_first_name,
               a.email as assigned_email, a.first_name as assigned_first_name
        FROM reports r
        LEFT JOIN travel_tickets t ON r.ticket_id = t.id
        JOIN users u ON r.user_id = u.id
        LEFT JOIN users a ON r.assigned_to = a.id
        WHERE r.id = %s
        """,
        (report_id,),
        fetch_one=True
    )
    
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found"
        )
    
    if (current_user["user_id"] != report["user_id"] and 
        not has_permission(current_user, ["admin", "support_agent"])):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this report"
        )
    
    await close_db()
    
    return report

@router.get("/admin/all", response_model=List[ReportResponse])
async def get_all_reports(
    status_filter: Optional[str] = None,
    category: Optional[str] = None,
    assigned_to: Optional[int] = None,
    user_id: Optional[int] = None,
    ticket_id: Optional[int] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    skip: int = 0,
    limit: int = 100,
    current_user: dict = Depends(require_roles("admin", "support_agent"))
):
    await connect_db()
    query = """
    SELECT r.*, 
           u.email as user_email, u.first_name as user_first_name,
           t.id as ticket_id, a.email as assigned_email
    FROM reports r
    JOIN users u ON r.user_id = u.id
    LEFT JOIN travel_tickets t ON r.ticket_id = t.id
    LEFT JOIN users a ON r.assigned_to = a.id
    WHERE 1=1
    """
    params = []
    
    if status_filter:
        query += " AND r.status = %s"
        params.append(status_filter)
    
    if category:
        query += " AND r.category = %s"
        params.append(category)
    
    if assigned_to:
        query += " AND r.assigned_to = %s"
        params.append(assigned_to)
    
    if user_id:
        query += " AND r.user_id = %s"
        params.append(user_id)
    
    if ticket_id:
        query += " AND r.ticket_id = %s"
        params.append(ticket_id)
    
    if start_date:
        query += " AND r.created_at >= %s"
        params.append(start_date)
    
    if end_date:
        query += " AND r.created_at <= %s"
        params.append(end_date)
    
    query += " ORDER BY r.created_at DESC LIMIT %s OFFSET %s"
    params.extend([limit, skip])
    
    reports = await execute_query(query, params, fetch_all=True)
    await close_db()
    return reports

@router.get("/admin/stats", response_model=ReportStatsResponse)
async def get_report_stats(
    time_range: Optional[str] = Query(None, description="Time range: today, week, month, year"),
    current_user: dict = Depends(require_roles("admin", "support_agent"))
):
    base_query = "SELECT COUNT(*) as count, status FROM reports"
    time_conditions = {
        "today": "DATE(created_at) = CURRENT_DATE",
        "week": "created_at >= DATE_SUB(CURRENT_DATE, INTERVAL 7 DAY)",
        "month": "created_at >= DATE_SUB(CURRENT_DATE, INTERVAL 1 MONTH)",
        "year": "created_at >= DATE_SUB(CURRENT_DATE, INTERVAL 1 YEAR)"
    }
    
    where_clause = f" WHERE {time_conditions[time_range]}" if time_range else ""
    
    status_counts = await execute_query(
        f"{base_query}{where_clause} GROUP BY status",
        fetch_all=True
    )
    
    category_counts = await execute_query(
        f"SELECT category, COUNT(*) as count FROM reports{where_clause} GROUP BY category",
        fetch_all=True
    )
    
    stats = {
        "total_reports": 0,
        "pending": 0,
        "reviewed": 0,
        "resolved": 0,
        "by_category": {}
    }
    
    for row in status_counts:
        stats["total_reports"] += row["count"]
        stats[row["status"]] = row["count"]
    
    for row in category_counts:
        stats["by_category"][row["category"]] = row["count"]
    
    return stats

@router.patch("/{report_id}", response_model=ReportResponse)
async def update_report(
    report_id: int,
    update: ReportUpdate,
    current_user: dict = Depends(require_roles("admin", "support_agent"))
):
    report = await execute_query(
        "SELECT * FROM reports WHERE id = %s",
        (report_id,),
        fetch_one=True
    )
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found"
        )

    set_clause = []
    params = []
    
    if update.status:
        valid_statuses = ["pending", "reviewed", "resolved"]
        if update.status not in valid_statuses:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
            )
        set_clause.append("status = %s")
        params.append(update.status)
    
    if update.resolution:
        set_clause.append("resolution = %s")
        params.append(update.resolution)
    
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
    
    if not set_clause:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields to update"
        )
    
    params.append(report_id)
    
    try:
        await execute_query(
            f"UPDATE reports SET {', '.join(set_clause)} WHERE id = %s",
            params,
            commit=True
        )
        return await execute_query(
            "SELECT * FROM reports WHERE id = %s",
            (report_id,),
            fetch_one=True
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.delete("/{report_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_report(
    report_id: int,
    current_user: dict = Depends(require_roles("admin"))
):
    report = await execute_query(
        "SELECT 1 FROM reports WHERE id = %s",
        (report_id,),
        fetch_one=True
    )
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found"
        )

    try:
        await execute_query(
            "DELETE FROM reports WHERE id = %s",
            (report_id,),
            commit=True
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/{report_id}/comments", status_code=status.HTTP_201_CREATED)
async def add_report_comment(
    report_id: int,
    comment: str,
    current_user: dict = Depends(get_current_user)
):
    report = await execute_query(
        "SELECT user_id FROM reports WHERE id = %s",
        (report_id,),
        fetch_one=True
    )
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found"
        )
    
    if (current_user["user_id"] != report["user_id"] and 
        not has_permission(current_user, ["admin", "support_agent"])):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to comment on this report"
        )

    try:
        await execute_query(
            """
            INSERT INTO report_comments (
                report_id, user_id, comment
            ) VALUES (%s, %s, %s)
            """,
            (report_id, current_user["user_id"], comment),
            commit=True
        )
        return {"message": "Comment added successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/{report_id}/comments", response_model=List[dict])
async def get_report_comments(
    report_id: int,
    current_user: dict = Depends(get_current_user)
):
    report = await execute_query(
        "SELECT user_id FROM reports WHERE id = %s",
        (report_id,),
        fetch_one=True
    )
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found"
        )
    
    if (current_user["user_id"] != report["user_id"] and 
        not has_permission(current_user, ["admin", "support_agent"])):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view comments for this report"
        )

    comments = await execute_query(
        """
        SELECT rc.*, u.email, u.first_name, u.last_name
        FROM report_comments rc
        JOIN users u ON rc.user_id = u.id
        WHERE rc.report_id = %s
        ORDER BY rc.created_at
        """,
        (report_id,),
        fetch_all=True
    )
    return comments