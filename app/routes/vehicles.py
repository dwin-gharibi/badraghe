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
            """,
            (
                detail.ticket_id, detail.airline_name, detail.flight_class.value,
                detail.stops, detail.flight_number, detail.departure_airport,
                detail.arrival_airport
            ),
            fetch_one=True,
            return_lastrowid=True
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

@router.post("/train-details", status_code=status.HTTP_201_CREATED)
async def create_train_details(
    detail: TrainDetailCreate,
    current_user: dict = Depends(require_roles("admin", "provider"))
):
    await _verify_ticket(detail.ticket_id, "train")
    await connect_db()
    try:
        detail_id = await execute_query(
            """
            INSERT INTO train_details (
                ticket_id, train_star_rating, private_cabin
            ) VALUES (%s, %s, %s)
            """,
            (
                detail.ticket_id,
                detail.train_star_rating,
                detail.private_cabin
            ),
            fetch_one=True,
            return_lastrowid=True
        )
        await close_db()
        return {"detail_id": detail_id["id"]}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/train-details/{ticket_id}", response_model=Dict[str, Any])
async def get_train_details(
    ticket_id: int,
    current_user: dict = Depends(get_current_user)
):
    await _verify_ticket(ticket_id, "train")
    await connect_db()

    details = await execute_query(
        "SELECT * FROM train_details WHERE ticket_id = %s",
        (ticket_id,),
        fetch_one=True
    )
    if not details:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Train details not found for this ticket"
        )
    
    features = await execute_query(
        """
        SELECT f.id, f.name, f.description
        FROM train_features tf
        JOIN features f ON tf.feature_id = f.id
        WHERE tf.train_id = %s
        """,
        (details["id"],),
        fetch_all=True
    )
    await close_db()
    details["features"] = features
    return details

@router.patch("/train-details/{ticket_id}", response_model=Dict[str, Any])
async def update_train_details(
    ticket_id: int,
    update_data: TrainDetailUpdate,
    current_user: dict = Depends(require_roles("admin", "provider"))
):
    await _verify_ticket(ticket_id, "train")
    await connect_db()

    update_values = update_data.dict(exclude_unset=True)
    if not update_values:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields to update"
        )
    
    set_clause = ", ".join([f"{field} = %s" for field in update_values.keys()])
    values = list(update_values.values())
    values.append(ticket_id)
    
    try:
        await execute_query(
            f"""
            UPDATE train_details 
            SET {set_clause}
            WHERE ticket_id = %s
            """,
            values,
            commit=True
        )
        await close_db()
        return await get_train_details(ticket_id, current_user)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/bus-details", status_code=status.HTTP_201_CREATED)
async def create_bus_details(
    detail: BusDetailCreate,
    current_user: dict = Depends(require_roles("admin", "provider"))
):
    await _verify_ticket(detail.ticket_id, "bus")
    await connect_db()

    try:
        detail_id = await execute_query(
            """
            INSERT INTO bus_details (
                ticket_id, bus_company, bus_type, seats_per_row
            ) VALUES (%s, %s, %s, %s)
            """,
            (
                detail.ticket_id,
                detail.bus_company,
                detail.bus_type.value,
                detail.seats_per_row.value
            ),
            fetch_one=True,
            return_lastrowid=True
        )
        await close_db()
        return {"detail_id": detail_id["id"]}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/bus-details/{ticket_id}", response_model=Dict[str, Any])
async def get_bus_details(
    ticket_id: int,
    current_user: dict = Depends(get_current_user)
):
    await _verify_ticket(ticket_id, "bus")
    await connect_db()

    details = await execute_query(
        "SELECT * FROM bus_details WHERE ticket_id = %s",
        (ticket_id,),
        fetch_one=True
    )
    if not details:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bus details not found for this ticket"
        )
    
    features = await execute_query(
        """
        SELECT f.id, f.name, f.description
        FROM bus_features bf
        JOIN features f ON bf.feature_id = f.id
        WHERE bf.bus_id = %s
        """,
        (details["id"],),
        fetch_all=True
    )
    await close_db()
    details["features"] = features
    return details

@router.put("/bus-details/{ticket_id}", response_model=Dict[str, Any])
async def update_bus_details(
    ticket_id: int,
    update_data: BusDetailUpdate,
    current_user: dict = Depends(require_roles("admin", "provider"))
):
    await _verify_ticket(ticket_id, "bus")
    await connect_db()

    update_values = update_data.dict(exclude_unset=True)
    if not update_values:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields to update"
        )
    
    if "bus_type" in update_values:
        update_values["bus_type"] = update_values["bus_type"].value
    if "seats_per_row" in update_values:
        update_values["seats_per_row"] = update_values["seats_per_row"].value
    
    set_clause = ", ".join([f"{field} = %s" for field in update_values.keys()])
    values = list(update_values.values())
    values.append(ticket_id)
    
    try:
        await execute_query(
            f"""
            UPDATE bus_details 
            SET {set_clause}
            WHERE ticket_id = %s
            """,
            values,
            commit=True
        )
        await close_db()
        return await get_bus_details(ticket_id, current_user)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/features", status_code=status.HTTP_201_CREATED)
async def create_feature(
    feature: FeatureCreate,
    current_user: dict = Depends(require_roles("admin", "provider"))
):
    try:
        await connect_db()
        feature_id = await execute_query(
            """
            INSERT INTO features (name, description)
            VALUES (%s, %s)
            """,
            (feature.name, feature.description),
            fetch_one=True,
            return_lastrowid=True
        )
        await close_db()
        return {"feature_id": feature_id["id"]}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/features", response_model=List[Dict[str, Any]])
async def get_all_features(
    search: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    current_user: dict = Depends(get_current_user)
):
    await connect_db()
    query = "SELECT id, name, description FROM features"
    params = []
    
    if search:
        query += " WHERE name LIKE %s OR description LIKE %s"
        params.extend([f"%{search}%", f"%{search}%"])
    
    query += " LIMIT %s OFFSET %s"
    params.extend([limit, skip])
    
    features = await execute_query(query, params, fetch_all=True)
    await close_db()
    return features

@router.post("/features/assign", status_code=status.HTTP_200_OK)
async def assign_feature_to_vehicle(
    assignment: FeatureAssignment,
    current_user: dict = Depends(require_roles("admin", "provider"))
):
    await connect_db()
    feature = await execute_query(
        "SELECT 1 FROM features WHERE id = %s",
        (assignment.feature_id,),
        fetch_one=True
    )
    if not feature:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Feature not found"
        )
    
    table_map = {
        "flight": ("flight_details", "flight_features", "flight_id"),
        "train": ("train_details", "train_features", "train_id"),
        "bus": ("bus_details", "bus_features", "bus_id")
    }
    
    if assignment.vehicle_type not in table_map:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid vehicle type. Must be 'flight', 'train', or 'bus'"
        )
    
    table_name, feature_table, fk_name = table_map[assignment.vehicle_type]
    
    vehicle = await execute_query(
        f"SELECT 1 FROM {table_name} WHERE id = %s",
        (assignment.vehicle_id,),
        fetch_one=True
    )
    if not vehicle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{assignment.vehicle_type.capitalize()} not found"
        )
    
    try:
        await execute_query(
            f"""
            INSERT IGNORE INTO {feature_table} ({fk_name}, feature_id)
            VALUES (%s, %s)
            """,
            (assignment.vehicle_id, assignment.feature_id),
            commit=True
        )
        await close_db()
        return {"message": f"Feature assigned to {assignment.vehicle_type} successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.delete("/features/unassign", status_code=status.HTTP_200_OK)
async def unassign_feature_from_vehicle(
    vehicle_type: str,
    vehicle_id: int,
    feature_id: int,
    current_user: dict = Depends(require_roles("admin", "provider"))
):
    await connect_db()
    table_map = {
        "flight": "flight_features",
        "train": "train_features",
        "bus": "bus_features"
    }
    
    if vehicle_type not in table_map:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid vehicle type. Must be 'flight', 'train', or 'bus'"
        )
    
    affected = await execute_query(
        f"""
        DELETE FROM {table_map[vehicle_type]} 
        WHERE feature_id = %s AND {table_map[vehicle_type][:5]}_id = %s
        """,
        (feature_id, vehicle_id),
        commit=True
    )
    if not affected:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Feature assignment not found"
        )
    await close_db()
    return {"message": "Feature unassigned successfully"}

@router.get("/features/assigned", response_model=List[Dict[str, Any]])
async def get_assigned_features(
    vehicle_type: str,
    vehicle_id: int,
    current_user: dict = Depends(get_current_user)
):
    table_map = {
        "flight": ("flight_features", "flight_id"),
        "train": ("train_features", "train_id"),
        "bus": ("bus_features", "bus_id")
    }
    await connect_db()

    if vehicle_type not in table_map:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid vehicle type. Must be 'flight', 'train', or 'bus'"
        )
    
    features = await execute_query(
        f"""
        SELECT f.id, f.name, f.description
        FROM {table_map[vehicle_type][0]} ff
        JOIN features f ON ff.feature_id = f.id
        WHERE ff.{table_map[vehicle_type][1]} = %s
        """,
        (vehicle_id,),
        fetch_all=True
    )
    await connect_db()
    return features

@router.get("/statistics/flights", response_model=Dict[str, Any])
async def get_flight_statistics(
    airline: Optional[str] = None,
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    current_user: dict = Depends(require_roles("admin", "analyst"))
):
    await connect_db()
    query = """
    SELECT 
        COUNT(*) as total_flights,
        AVG(t.price) as avg_price,
        MIN(t.price) as min_price,
        MAX(t.price) as max_price,
        SUM(CASE WHEN t.status = 'available' THEN 1 ELSE 0 END) as available_flights,
        SUM(CASE WHEN t.status = 'sold_out' THEN 1 ELSE 0 END) as sold_out_flights
    FROM flight_details fd
    JOIN travel_tickets t ON fd.ticket_id = t.id
    WHERE 1=1
    """
    params = []
    
    if airline:
        query += " AND fd.airline_name LIKE %s"
        params.append(f"%{airline}%")
    
    if from_date:
        query += " AND t.departure_time >= %s"
        params.append(from_date)
    
    if to_date:
        query += " AND t.departure_time <= %s"
        params.append(to_date)
    
    stats = await execute_query(query, params, fetch_one=True)
    await close_db()
    return stats

@router.get("/statistics/trains", response_model=Dict[str, Any])
async def get_train_statistics(
    min_rating: Optional[int] = None,
    max_rating: Optional[int] = None,
    current_user: dict = Depends(require_roles("admin", "analyst"))
):
    await connect_db()
    query = """
    SELECT 
        COUNT(*) as total_trains,
        AVG(td.train_star_rating) as avg_rating,
        SUM(CASE WHEN td.private_cabin = TRUE THEN 1 ELSE 0 END) as with_private_cabins,
        AVG(t.price) as avg_price,
        MIN(t.price) as min_price,
        MAX(t.price) as max_price
    FROM train_details td
    JOIN travel_tickets t ON td.ticket_id = t.id
    WHERE 1=1
    """
    params = []
    
    if min_rating is not None:
        query += " AND td.train_star_rating >= %s"
        params.append(min_rating)
    
    if max_rating is not None:
        query += " AND td.train_star_rating <= %s"
        params.append(max_rating)
    
    stats = await execute_query(query, params, fetch_one=True)
    await close_db()
    return stats

@router.get("/statistics/buses", response_model=Dict[str, Any])
async def get_bus_statistics(
    bus_type: Optional[str] = None,
    current_user: dict = Depends(require_roles("admin", "analyst"))
):
    await connect_db()
    query = """
    SELECT 
        COUNT(*) as total_buses,
        AVG(t.price) as avg_price,
        MIN(t.price) as min_price,
        MAX(t.price) as max_price,
        SUM(CASE WHEN bd.bus_type = 'VIP' THEN 1 ELSE 0 END) as vip_buses,
        SUM(CASE WHEN bd.bus_type = 'standard' THEN 1 ELSE 0 END) as standard_buses,
        SUM(CASE WHEN bd.bus_type = 'sleeper' THEN 1 ELSE 0 END) as sleeper_buses
    FROM bus_details bd
    JOIN travel_tickets t ON bd.ticket_id = t.id
    WHERE 1=1
    """
    params = []
    
    if bus_type:
        query += " AND bd.bus_type = %s"
        params.append(bus_type)
    
    stats = await execute_query(query, params, fetch_one=True)
    await close_db()
    return stats