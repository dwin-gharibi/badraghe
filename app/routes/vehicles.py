from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, validator
from datetime import datetime
from enum import Enum
from app.db import execute_query, close_db, connect_db
from app.utils.auth_util import get_current_user, require_roles
from app.utils.rbac_util import has_permission

router = APIRouter(prefix="/vehicles")

class FlightClass(str, Enum):
    economy = "economy"
    business = "business"
    first_class = "first_class"

class BusType(str, Enum):
    VIP = "VIP"
    standard = "standard"
    sleeper = "sleeper"

class SeatConfig(str, Enum):
    one_plus_two = "1+2"
    two_plus_two = "2+2"

class FlightDetailBase(BaseModel):
    airline_name: str = Field(..., max_length=100)
    flight_class: FlightClass
    stops: int = Field(0, ge=0, le=5)
    flight_number: str = Field(..., max_length=20)
    departure_airport: str = Field(..., max_length=100)
    arrival_airport: str = Field(..., max_length=100)

class FlightDetailCreate(FlightDetailBase):
    ticket_id: int

class FlightDetailUpdate(BaseModel):
    airline_name: Optional[str] = Field(None, max_length=100)
    flight_class: Optional[FlightClass]
    stops: Optional[int] = Field(None, ge=0, le=5)
    flight_number: Optional[str] = Field(None, max_length=20)
    departure_airport: Optional[str] = Field(None, max_length=100)
    arrival_airport: Optional[str] = Field(None, max_length=100)

class TrainDetailBase(BaseModel):
    train_star_rating: int = Field(0, ge=0, le=5)
    private_cabin: bool = False

class TrainDetailCreate(TrainDetailBase):
    ticket_id: int

class TrainDetailUpdate(BaseModel):
    train_star_rating: Optional[int] = Field(None, ge=0, le=5)
    private_cabin: Optional[bool]

class BusDetailBase(BaseModel):
    bus_company: str = Field(..., max_length=100)
    bus_type: BusType
    seats_per_row: SeatConfig

class BusDetailCreate(BusDetailBase):
    ticket_id: int

class BusDetailUpdate(BaseModel):
    bus_company: Optional[str] = Field(None, max_length=100)
    bus_type: Optional[BusType]
    seats_per_row: Optional[SeatConfig]

class FeatureAssignment(BaseModel):
    feature_id: int
    vehicle_id: int
    vehicle_type: str

class FeatureCreate(BaseModel):
    name: str = Field(..., max_length=100)
    description: Optional[str] = None

async def _verify_ticket(ticket_id: int, transport_type: str):
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
    if ticket["transport_type"] != transport_type:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ticket is not a {transport_type}"
        )
    await close_db()

@router.post("/flight-details", status_code=status.HTTP_201_CREATED)
async def create_flight_details(
    detail: FlightDetailCreate,
    current_user: dict = Depends(require_roles("admin", "provider"))
):
    await _verify_ticket(detail.ticket_id, "plane")
    await connect_db()
    try:
        detail_id = await execute_query(
            """
            INSERT INTO flight_details (
                ticket_id, airline_name, flight_class,
                stops, flight_number, departure_airport,
                arrival_airport
            ) VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING id
            """,
            (
                detail.ticket_id, detail.airline_name, detail.flight_class.value,
                detail.stops, detail.flight_number, detail.departure_airport,
                detail.arrival_airport
            ),
            fetch_one=True
        )
        await close_db()
        return {"detail_id": detail_id["id"]}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    
@router.get("/flight-details/{ticket_id}", response_model=Dict[str, Any])
async def get_flight_details(
    ticket_id: int,
    current_user: dict = Depends(get_current_user)
):
    await _verify_ticket(ticket_id, "plane")
    await connect_db()
    details = await execute_query(
        """
        SELECT * FROM flight_details 
        WHERE ticket_id = %s
        """,
        (ticket_id,),
        fetch_one=True
    )
    if not details:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Flight details not found for this ticket"
        )
    
    features = await execute_query(
        """
        SELECT f.id, f.name, f.description
        FROM flight_features ff
        JOIN features f ON ff.feature_id = f.id
        WHERE ff.flight_id = %s
        """,
        (details["id"],),
        fetch_all=True
    )
    
    details["features"] = features
    await close_db()

    return details

@router.put("/flight-details/{ticket_id}", response_model=Dict[str, Any])
async def update_flight_details(
    ticket_id: int,
    update_data: FlightDetailUpdate,
    current_user: dict = Depends(require_roles("admin", "provider"))
):
    await _verify_ticket(ticket_id, "plane")
    await connect_db()

    existing = await execute_query(
        "SELECT * FROM flight_details WHERE ticket_id = %s",
        (ticket_id,),
        fetch_one=True
    )
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Flight details not found"
        )
    
    update_values = update_data.dict(exclude_unset=True)
    if not update_values:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields to update"
        )
    
    if "flight_class" in update_values:
        update_values["flight_class"] = update_values["flight_class"].value
    
    set_clause = ", ".join([f"{field} = %s" for field in update_values.keys()])
    values = list(update_values.values())
    values.append(ticket_id)
    
    try:
        await execute_query(
            f"""
            UPDATE flight_details 
            SET {set_clause}
            WHERE ticket_id = %s
            """,
            values,
            commit=True
        )
        await close_db()
        return await get_flight_details(ticket_id, current_user)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
