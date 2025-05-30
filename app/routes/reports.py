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
