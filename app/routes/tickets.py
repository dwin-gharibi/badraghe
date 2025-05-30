from fastapi import Query, APIRouter, Path, HTTPException, status, Depends, Header
from typing import Optional, List, Dict
from pydantic import BaseModel
from enum import Enum
from datetime import datetime
from app.db import execute_query, connect_db, close_db
from app.redis import get_redis
from app.utils.auth_util import get_current_user, require_roles
import json
import hashlib
import httpx

router = APIRouter(prefix="/tickets")

CACHE_TTL = 300

class TransportType(str, Enum):
    PLANE = "plane"
    TRAIN = "train"
    BUS = "bus"

class TicketStatus(str, Enum):
    AVAILABLE = "available"
    SOLD_OUT = "sold_out"
    CANCELED = "canceled"

class TicketClass(str, Enum):
    ECONOMY = "economy"
    BUSINESS = "business"
    FIRST_CLASS = "first_class"
    VIP = "VIP"
    STANDARD = "standard"
    SLEEPER = "sleeper"

class TicketCreate(BaseModel):
    transport_type: TransportType
    departure_city: str
    arrival_city: str
    departure_time: datetime
    arrival_time: datetime
    price: float
    currency: str = "IRR"
    total_seats: int
    class_type: TicketClass
    transport_company_id: Optional[int] = None
    status: TicketStatus = TicketStatus.AVAILABLE

class TicketUpdate(BaseModel):
    departure_city: Optional[str] = None
    arrival_city: Optional[str] = None
    departure_time: Optional[datetime] = None
    arrival_time: Optional[datetime] = None
    price: Optional[float] = None
    available_seats: Optional[int] = None
    status: Optional[TicketStatus] = None
    class_type: Optional[TicketClass] = None

class FlightDetailsCreate(BaseModel):
    airline_name: str
    flight_class: TicketClass
    stops: int = 0
    flight_number: str
    departure_airport: str
    arrival_airport: str

class TrainDetailsCreate(BaseModel):
    train_star_rating: int = 0
    private_cabin: bool = False

class BusDetailsCreate(BaseModel):
    bus_company: str
    bus_type: TicketClass
    seats_per_row: str = "2+2"

class TicketResponse(BaseModel):
    id: int
    transport_type: TransportType
    departure_city: str
    arrival_city: str
    departure_time: datetime
    arrival_time: datetime
    price: float
    currency: str
    available_seats: int
    total_seats: int
    transport_company_id: Optional[int] = None
    class_type: TicketClass
    status: TicketStatus
    company_name: Optional[str] = None
    details: Optional[dict] = None
    features: Optional[List[str]] = None

class TicketStatsResponse(BaseModel):
    total_tickets: int
    available: int
    sold_out: int
    canceled: int
    by_transport_type: Dict[str, int]
    by_class: Dict[str, int]

async def generate_cache_key(params: dict) -> str:
    return "tickets:" + hashlib.md5(json.dumps(params, sort_keys=True).encode()).hexdigest()

async def get_ticket_with_details(ticket_id: int) -> Optional[dict]:
    await connect_db()
    ticket = await execute_query(
        """
        SELECT tt.*, sp.name AS company_name
        FROM travel_tickets tt
        LEFT JOIN service_providers sp ON tt.transport_company_id = sp.id
        WHERE tt.id = %s
        """,
        (ticket_id,),
        fetch_one=True
    )
    
    if not ticket:
        return None
    
    details = None
    features = []
    if ticket["transport_type"] == "plane":
        details = await execute_query(
            "SELECT * FROM flight_details WHERE ticket_id = %s", 
            (ticket_id,), 
            fetch_one=True
        )
        if details:
            features = await execute_query(
                """
                SELECT f.name FROM features f
                JOIN flight_features ff ON f.id = ff.feature_id
                WHERE ff.flight_id = %s
                """,
                (details["id"],),
                fetch_all=True
            )
    elif ticket["transport_type"] == "train":
        details = await execute_query(
            "SELECT * FROM train_details WHERE ticket_id = %s", 
            (ticket_id,), 
            fetch_one=True
        )
        if details:
            features = await execute_query(
                """
                SELECT f.name FROM features f
                JOIN train_features tf ON f.id = tf.feature_id
                WHERE tf.train_id = %s
                """,
                (details["id"],),
                fetch_all=True
            )
    elif ticket["transport_type"] == "bus":
        details = await execute_query(
            "SELECT * FROM bus_details WHERE ticket_id = %s", 
            (ticket_id,), 
            fetch_one=True
        )
        if details:
            features = await execute_query(
                """
                SELECT f.name FROM features f
                JOIN bus_features bf ON f.id = bf.feature_id
                WHERE bf.bus_id = %s
                """,
                (details["id"],),
                fetch_all=True
            )
    
    ticket["features"] = [f["name"] for f in features] if features else []
    ticket["details"] = details
    
    await close_db()
    return ticket

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=TicketResponse)
async def create_ticket(
    ticket: TicketCreate,
    current_user: dict = Depends(require_roles("admin", "ticket_manager"))
):
    await connect_db()
    if ticket.transport_company_id:
        company = await execute_query(
            "SELECT 1 FROM service_providers WHERE id = %s",
            (ticket.transport_company_id,),
            fetch_one=True
        )
        if not company:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Transport company not found"
            )
    
    if ticket.total_seats <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Total seats must be greater than 0"
        )
    
    try:
        ticket_id = await execute_query(
            """
            INSERT INTO travel_tickets (
                transport_type, departure_city, arrival_city,
                departure_time, arrival_time, price, currency,
                total_seats, available_seats, transport_company_id,
                class_type, status
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
            """,
            (
                ticket.transport_type.value,
                ticket.departure_city,
                ticket.arrival_city,
                ticket.departure_time,
                ticket.arrival_time,
                ticket.price,
                ticket.currency,
                ticket.total_seats,
                ticket.total_seats,
                ticket.transport_company_id,
                ticket.class_type.value,
                ticket.status.value
            ),
            fetch_one=True
        )
        await close_db()
        return await get_ticket_with_details(ticket_id["id"])
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/{ticket_id}", response_model=TicketResponse)
async def get_ticket(
    ticket_id: int = Path(..., title="The ID of the ticket to get"),
    current_user: dict = Depends(get_current_user)
):
    await connect_db()
    ticket = await get_ticket_with_details(ticket_id)
    
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found"
        )
    
    await close_db()
    return ticket

@router.head("/{ticket_id}")
async def check_ticket_exists(
    ticket_id: int,
    current_user: dict = Depends(get_current_user)
):
    await close_db()
    ticket = await execute_query(
        "SELECT 1 FROM travel_tickets WHERE id = %s",
        (ticket_id,),
        fetch_one=True
    )
    
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found"
        )
    
    await close_db()
    return {}

@router.put("/{ticket_id}", response_model=TicketResponse)
async def update_ticket(
    ticket_id: int,
    update: TicketUpdate,
    current_user: dict = Depends(require_roles("admin", "ticket_manager"))
):
    await connect_db()
    ticket = await execute_query(
        "SELECT * FROM travel_tickets WHERE id = %s",
        (ticket_id,),
        fetch_one=True
    )
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found"
        )
    
    set_clause = []
    params = []
    
    if update.departure_city:
        set_clause.append("departure_city = %s")
        params.append(update.departure_city)
    
    if update.arrival_city:
        set_clause.append("arrival_city = %s")
        params.append(update.arrival_city)
    
    if update.departure_time:
        set_clause.append("departure_time = %s")
        params.append(update.departure_time)
    
    if update.arrival_time:
        set_clause.append("arrival_time = %s")
        params.append(update.arrival_time)
    
    if update.price is not None:
        if update.price < 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Price cannot be negative"
            )
        set_clause.append("price = %s")
        params.append(update.price)
    
    if update.available_seats is not None:
        if update.available_seats < 0 or update.available_seats > ticket["total_seats"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Available seats must be between 0 and {ticket['total_seats']}"
            )
        set_clause.append("available_seats = %s")
        params.append(update.available_seats)
    
    if update.status:
        set_clause.append("status = %s")
        params.append(update.status.value)
    
    if update.class_type:
        set_clause.append("class_type = %s")
        params.append(update.class_type.value)
    
    if not set_clause:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields to update"
        )
    
    params.append(ticket_id)
    
    try:
        await execute_query(
            f"UPDATE travel_tickets SET {', '.join(set_clause)} WHERE id = %s",
            params,
            commit=True
        )
        
        redis = await get_redis()
        await redis.delete(f"ticket:{ticket_id}")
        
        await close_db()
        return await get_ticket_with_details(ticket_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.delete("/{ticket_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_ticket(
    ticket_id: int,
    current_user: dict = Depends(require_roles("admin", "ticket_manager"))
):
    await connect_db()
    ticket = await execute_query(
        "SELECT * FROM travel_tickets WHERE id = %s",
        (ticket_id,),
        fetch_one=True
    )
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found"
        )
    
    active_reservations = await execute_query(
        "SELECT 1 FROM user_reservations WHERE ticket_id = %s AND status IN ('temporary', 'reserved', 'paid')",
        (ticket_id,),
        fetch_one=True
    )
    if active_reservations:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete ticket with active reservations"
        )
    
    try:
        if ticket["transport_type"] == "plane":
            await execute_query(
                "DELETE FROM flight_features WHERE flight_id IN (SELECT id FROM flight_details WHERE ticket_id = %s)",
                (ticket_id,),
                commit=True
            )
            await execute_query(
                "DELETE FROM flight_details WHERE ticket_id = %s",
                (ticket_id,),
                commit=True
            )
        elif ticket["transport_type"] == "train":
            await execute_query(
                "DELETE FROM train_features WHERE train_id IN (SELECT id FROM train_details WHERE ticket_id = %s)",
                (ticket_id,),
                commit=True
            )
            await execute_query(
                "DELETE FROM train_details WHERE ticket_id = %s",
                (ticket_id,),
                commit=True
            )
        elif ticket["transport_type"] == "bus":
            await execute_query(
                "DELETE FROM bus_features WHERE bus_id IN (SELECT id FROM bus_details WHERE ticket_id = %s)",
                (ticket_id,),
                commit=True
            )
            await execute_query(
                "DELETE FROM bus_details WHERE ticket_id = %s",
                (ticket_id,),
                commit=True
            )
        
        await execute_query(
            "DELETE FROM travel_tickets WHERE id = %s",
            (ticket_id,),
            commit=True
        )
        
        redis = await get_redis()
        await redis.delete(f"ticket:{ticket_id}")
        await redis.delete("tickets:*")
        await close_db()

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/search", response_model=List[TicketResponse])
async def search_tickets(
    departure_city: Optional[str] = Query(None),
    arrival_city: Optional[str] = Query(None),
    travel_date: Optional[str] = Query(None),
    transport_type: Optional[TransportType] = Query(None),
    price_min: Optional[float] = Query(None, ge=0),
    price_max: Optional[float] = Query(None, ge=0),
    company_name: Optional[str] = Query(None),
    departure_time: Optional[str] = Query(None),
    class_type: Optional[TicketClass] = Query(None),
    skip: int = 0,
    limit: int = 100,
    current_user: dict = Depends(get_current_user)
):
    if not any([departure_city, arrival_city, travel_date, transport_type, 
               price_min, price_max, company_name, departure_time, class_type]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one query parameter must be provided."
        )
    await connect_db()
    redis = await get_redis()
    cache_params = {
        "departure_city": departure_city,
        "arrival_city": arrival_city,
        "travel_date": travel_date,
        "transport_type": transport_type.value if transport_type else None,
        "price_min": price_min,
        "price_max": price_max,
        "company_name": company_name,
        "departure_time": departure_time,
        "class_type": class_type.value if class_type else None,
        "skip": skip,
        "limit": limit
    }
    cache_key = await generate_cache_key(cache_params)
    
    cached = await redis.get(cache_key)
    if cached:
        return json.loads(cached)
    
    query = """
    SELECT tt.*, sp.name AS company_name
    FROM travel_tickets tt
    LEFT JOIN service_providers sp ON tt.transport_company_id = sp.id
    WHERE tt.status = 'available'
    """
    params = []
    
    if departure_city:
        query += " AND tt.departure_city = %s"
        params.append(departure_city)
    
    if arrival_city:
        query += " AND tt.arrival_city = %s"
        params.append(arrival_city)
    
    if travel_date:
        query += " AND DATE(tt.departure_time) = %s"
        params.append(travel_date)
    
    if transport_type:
        query += " AND tt.transport_type = %s"
        params.append(transport_type.value)
    
    if price_min is not None:
        query += " AND tt.price >= %s"
        params.append(price_min)
    
    if price_max is not None:
        query += " AND tt.price <= %s"
        params.append(price_max)
    
    if company_name:
        query += " AND sp.name = %s"
        params.append(company_name)
    
    if departure_time:
        query += " AND TIME(tt.departure_time) >= %s"
        params.append(departure_time)
    
    if class_type:
        query += " AND tt.class_type = %s"
        params.append(class_type.value)
    
    query += " ORDER BY tt.departure_time ASC LIMIT %s OFFSET %s"
    params.extend([limit, skip])
    
    tickets = await execute_query(query, tuple(params), fetch_all=True)
    
    detailed_tickets = []
    for ticket in tickets:
        ticket_details = await get_ticket_with_details(ticket["id"])
        if ticket_details:
            detailed_tickets.append(ticket_details)
    
    await redis.set(cache_key, json.dumps(detailed_tickets, default=str), ex=CACHE_TTL)
    await close_db()

    return detailed_tickets

