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

