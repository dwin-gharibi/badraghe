from fastapi import Query, APIRouter, Path, HTTPException, status, Depends
from typing import Optional, List, Dict
from pydantic import BaseModel
from enum import Enum
from datetime import datetime
from app.db import execute_query, connect_db, close_db
from app.redis import get_redis
from app.utils.cache_util import get_cache, set_cache, delete_cache
from app.utils.auth_util import get_current_user, require_roles
from app.utils.elastic_util import index_ticket, delete_ticket_index, search_tickets_es
import json
import hashlib

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
    FIRST_CLASS = "first"
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

@router.get("/search", response_model=List[TicketResponse])
async def search_tickets(
    departure_city: Optional[str] = None,
    arrival_city: Optional[str] = None,
    travel_date: Optional[str] = None,
    transport_type: Optional[TransportType] = None,
    price_min: Optional[float] = None,
    price_max: Optional[float] = None,
    company_name: Optional[str] = None,
    departure_time: Optional[str] = None,
    class_type: Optional[TicketClass] = None,
    status: Optional[TicketStatus] = TicketStatus.AVAILABLE,
    skip: int = 0,
    limit: int = 100
) -> List[dict]:
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
        "status": status.value if status else None,
        "skip": skip,
        "limit": limit
    }
    cache_key = await generate_cache_key(cache_params)
    cached = await get_cache(cache_key)
    if cached:
        return json.loads(cached)
    try:
        tickets, total = await search_tickets_es(cache_params)
        await set_cache(cache_key, json.dumps(tickets, default=str), expire_seconds=300)
        return tickets
    except Exception as e:
        await connect_db()
        query = """
            SELECT tt.*, sp.name AS company_name
            FROM travel_tickets tt
            LEFT JOIN service_providers sp ON tt.transport_company_id = sp.id
            WHERE 1=1
        """
        params = []
        if status:
            query += " AND tt.status = %s"
            params.append(status.value)
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
        await set_cache(cache_key, json.dumps(detailed_tickets, default=str), expire_seconds=300)
        await close_db()
        return detailed_tickets
    
@router.get("/stats", response_model=TicketStatsResponse)
async def get_ticket_stats(
    transport_type: Optional[TransportType] = None,
    class_type: Optional[TicketClass] = None,
):
    where_clause = "WHERE 1=1"
    params = []

    if transport_type:
        where_clause += " AND transport_type = %s"
        params.append(transport_type.value)
    if class_type:
        where_clause += " AND class_type = %s"
        params.append(class_type.value)

    await connect_db()
    status_counts = await execute_query(
        f"""
        SELECT status, COUNT(*) as count
        FROM travel_tickets
        {where_clause}
        GROUP BY status
        """,
        params,
        fetch_all=True
    )
    await connect_db()
    transport_counts = await execute_query(
        f"""
        SELECT transport_type, COUNT(*) as count
        FROM travel_tickets
        WHERE status = 'available'
        GROUP BY transport_type
        """,
        fetch_all=True
    )
    await connect_db()
    class_counts = await execute_query(
        f"""
        SELECT class_type, COUNT(*) as count
        FROM travel_tickets
        WHERE status = 'available'
        GROUP BY class_type
        """,
        fetch_all=True
    )
    stats = {
        "total_tickets": 0,
        "available": 0,
        "sold_out": 0,
        "canceled": 0,
        "by_transport_type": {},
        "by_class": {}
    }
    for row in status_counts:
        stats["total_tickets"] += row["count"]
        stats[row["status"]] = row["count"]
    for row in transport_counts:
        stats["by_transport_type"][row["transport_type"]] = row["count"]
    for row in class_counts:
        stats["by_class"][row["class_type"]] = row["count"]
    return stats


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
            fetch_one=True,
            return_lastrowid=True
        )
        ticket_details = await get_ticket_with_details(ticket_id)
        await index_ticket(ticket_details)
        await close_db()
        return ticket_details
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
    ticket = await get_ticket_with_details(ticket_id)
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found"
        )
    return ticket

@router.head("/{ticket_id}")
async def check_ticket_exists(
    ticket_id: int,
    current_user: dict = Depends(get_current_user)
):
    await connect_db()
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
    current_user: dict = Depends(require_roles("admin"))
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
        ticket_details = await get_ticket_with_details(ticket_id)
        await index_ticket(ticket_details)
        await close_db()
        return ticket_details
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
        await delete_ticket_index(ticket_id)
        await close_db()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/{ticket_id}/train-details", status_code=status.HTTP_201_CREATED)
async def add_train_details(
    ticket_id: int,
    details: TrainDetailsCreate,
    current_user: dict = Depends(require_roles("admin", "ticket_manager"))
):
    await connect_db()
    ticket = await execute_query(
        "SELECT transport_type FROM travel_tickets WHERE id = %s",
        (ticket_id,),
        fetch_one=True
    )
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found"
        )
    if ticket["transport_type"] != "train":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ticket is not a train"
        )
    
    existing = await execute_query(
        "SELECT 1 FROM train_details WHERE ticket_id = %s",
        (ticket_id,),
        fetch_one=True
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Train details already exist for this ticket"
        )
    
    try:
        await execute_query(
            """
            INSERT INTO train_details (
                ticket_id, train_star_rating, private_cabin
            ) VALUES (%s, %s, %s)
            """,
            (
                ticket_id,
                details.train_star_rating,
                details.private_cabin
            ),
            commit=True
        )
        
        redis = await get_redis()
        await redis.delete(f"ticket:{ticket_id}")
        await close_db()

        return {"message": "Train details added successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/{ticket_id}/bus-details", status_code=status.HTTP_201_CREATED)
async def add_bus_details(
    ticket_id: int,
    details: BusDetailsCreate,
    current_user: dict = Depends(require_roles("admin", "ticket_manager"))
):
    await connect_db()
    ticket = await execute_query(
        "SELECT transport_type FROM travel_tickets WHERE id = %s",
        (ticket_id,),
        fetch_one=True
    )
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found"
        )
    if ticket["transport_type"] != "bus":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ticket is not a bus"
        )
    
    existing = await execute_query(
        "SELECT 1 FROM bus_details WHERE ticket_id = %s",
        (ticket_id,),
        fetch_one=True
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bus details already exist for this ticket"
        )
    
    try:
        await execute_query(
            """
            INSERT INTO bus_details (
                ticket_id, bus_company, bus_type, seats_per_row
            ) VALUES (%s, %s, %s, %s)
            """,
            (
                ticket_id,
                details.bus_company,
                details.bus_type.value,
                details.seats_per_row
            ),
            commit=True
        )
        
        redis = await get_redis()
        await redis.delete(f"ticket:{ticket_id}")
        await close_db()
        
        return {"message": "Bus details added successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/{ticket_id}/features", status_code=status.HTTP_201_CREATED)
async def add_feature_to_ticket(
    ticket_id: int,
    feature_name: str,
    current_user: dict = Depends(require_roles("admin", "ticket_manager"))
):
    await connect_db()
    ticket = await execute_query(
        "SELECT transport_type FROM travel_tickets WHERE id = %s",
        (ticket_id,),
        fetch_one=True
    )
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found"
        )
    
    feature = await execute_query(
        "SELECT id FROM features WHERE name = %s",
        (feature_name,),
        fetch_one=True
    )
    if not feature:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Feature not found"
        )
    
    details_id = None
    if ticket["transport_type"] == "plane":
        details = await execute_query(
            "SELECT id FROM flight_details WHERE ticket_id = %s",
            (ticket_id,),
            fetch_one=True
        )
        if details:
            details_id = details["id"]
            table = "flight_features"
    elif ticket["transport_type"] == "train":
        details = await execute_query(
            "SELECT id FROM train_details WHERE ticket_id = %s",
            (ticket_id,),
            fetch_one=True
        )
        if details:
            details_id = details["id"]
            table = "train_features"
    elif ticket["transport_type"] == "bus":
        details = await execute_query(
            "SELECT id FROM bus_details WHERE ticket_id = %s",
            (ticket_id,),
            fetch_one=True
        )
        if details:
            details_id = details["id"]
            table = "bus_features"
    
    if not details_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ticket details not found"
        )
    
    existing = await execute_query(
        f"SELECT 1 FROM {table} WHERE {table.split('_')[0]}_id = %s AND feature_id = %s",
        (details_id, feature["id"]),
        fetch_one=True
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Feature already added to this ticket"
        )
    
    try:
        await execute_query(
            f"INSERT INTO {table} ({table.split('_')[0]}_id, feature_id) VALUES (%s, %s)",
            (details_id, feature["id"]),
            commit=True
        )
        
        redis = await get_redis()
        await redis.delete(f"ticket:{ticket_id}")
        await connect_db()

        return {"message": "Feature added successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
    
@router.post("/{ticket_id}/flight-details", status_code=status.HTTP_201_CREATED)
async def add_flight_details(
    ticket_id: int,
    details: FlightDetailsCreate,
    current_user: dict = Depends(require_roles("admin", "ticket_manager"))
):
    await connect_db()
    ticket = await execute_query(
        "SELECT transport_type FROM travel_tickets WHERE id = %s",
        (ticket_id,),
        fetch_one=True
    )
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found"
        )
    if ticket["transport_type"] != "plane":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ticket is not a flight"
        )
    
    existing = await execute_query(
        "SELECT 1 FROM flight_details WHERE ticket_id = %s",
        (ticket_id,),
        fetch_one=True
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Flight details already exist for this ticket"
        )
    
    try:
        await execute_query(
            """
            INSERT INTO flight_details (
                ticket_id, airline_name, flight_class,
                stops, flight_number, departure_airport,
                arrival_airport
            ) VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            (
                ticket_id,
                details.airline_name,
                details.flight_class.value,
                details.stops,
                details.flight_number,
                details.departure_airport,
                details.arrival_airport
            ),
            commit=True
        )
        
        redis = await get_redis()
        await redis.delete(f"ticket:{ticket_id}")
        await close_db()

        return {"message": "Flight details added successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

async def check_ticket_exists(ticket_id: int, current_user: dict = Depends(get_current_user)) -> bool:
    await connect_db()
    ticket = await execute_query(
        "SELECT 1 FROM travel_tickets WHERE id = %s AND status = 'available'",
        (ticket_id,),
        fetch_one=True
    )
    await close_db()
    return bool(ticket)