from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from pydantic import BaseModel, EmailStr
from app.db import execute_query, connect_db, close_db
from app.utils.auth_util import get_current_user, require_roles

router = APIRouter(prefix="/service-providers")

class ServiceProviderCreate(BaseModel):
    name: str
    contact_email: EmailStr
    contact_phone: str
    address: Optional[str] = None
    website_url: Optional[str] = None

class ServiceProviderUpdate(BaseModel):
    name: Optional[str] = None
    contact_email: Optional[EmailStr] = None
    contact_phone: Optional[str] = None
    address: Optional[str] = None
    website_url: Optional[str] = None

async def _get_provider(provider_id: int):
    await connect_db()
    provider = await execute_query(
        "SELECT * FROM service_providers WHERE id = %s",
        (provider_id,),
        fetch_one=True
    )
    if not provider:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service provider not found"
        )
    
    await close_db()
    return provider

@router.get("/", response_model=List[dict])
async def get_service_providers(
    name: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    _: dict = Depends(get_current_user)
):
    await connect_db()
    query = "SELECT * FROM service_providers WHERE 1=1"
    params = []
    
    if name:
        query += " AND name LIKE %s"
        params.append(f"%{name}%")
    
    query += " LIMIT %s OFFSET %s"
    params.extend([limit, skip])
    
    providers = await execute_query(query, params, fetch_all=True)
    await close_db()
    return providers

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_service_provider(
    provider: ServiceProviderCreate,
    current_user: dict = Depends(require_roles("admin"))
):
    try:
        await connect_db()
        provider_id = await execute_query(
            """
            INSERT INTO service_providers (
                name, contact_email, contact_phone, 
                address, website_url
            ) VALUES (%s, %s, %s, %s, %s)
            """,
            (
                provider.name, provider.contact_email, provider.contact_phone,
                provider.address, provider.website_url
            ),
            fetch_one=True,
            return_lastrowid=True
        )
        await close_db()
        return {"provider_id": provider_id["id"]}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/{provider_id}/tickets", response_model=List[dict])
async def get_provider_tickets(
    provider_id: int,
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    current_user: dict = Depends(get_current_user)
):
    await connect_db()
    query = """
    SELECT * FROM travel_tickets 
    WHERE transport_company_id = %s
    """
    params = [provider_id]
    
    if status:
        query += " AND status = %s"
        params.append(status)
    
    query += " LIMIT %s OFFSET %s"
    params.extend([limit, skip])
    
    tickets = await execute_query(query, params, fetch_all=True)
    await close_db()
    return tickets

@router.put("/{provider_id}", response_model=dict)
async def update_service_provider(
    provider_id: int,
    provider: ServiceProviderCreate,
    current_user: dict = Depends(require_roles("admin"))
):
    await connect_db()
    existing = await execute_query(
        "SELECT 1 FROM service_providers WHERE name = %s AND id != %s",
        (provider.name, provider_id),
        fetch_one=True
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Service provider with this name already exists"
        )

    try:
        await execute_query(
            """
            UPDATE service_providers 
            SET name = %s, contact_email = %s, contact_phone = %s,
                address = %s, website_url = %s
            WHERE id = %s
            """,
            (
                provider.name, provider.contact_email, provider.contact_phone,
                provider.address, provider.website_url, provider_id
            ),
            commit=True
        )
        await close_db()
        return await _get_provider(provider_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.patch("/{provider_id}", response_model=dict)
async def partial_update_service_provider(
    provider_id: int,
    provider: ServiceProviderUpdate,
    current_user: dict = Depends(require_roles("admin"))
):
    await connect_db()
    update_data = provider.dict(exclude_unset=True)
    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields to update"
        )

    if "name" in update_data:
        existing = await execute_query(
            "SELECT 1 FROM service_providers WHERE name = %s AND id != %s",
            (update_data["name"], provider_id),
            fetch_one=True
        )
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Service provider with this name already exists"
            )

    set_clause = ", ".join([f"{field} = %s" for field in update_data.keys()])
    values = list(update_data.values())
    values.append(provider_id)

    try:
        await execute_query(
            f"UPDATE service_providers SET {set_clause} WHERE id = %s",
            values,
            commit=True
        )
        await close_db()
        return await _get_provider(provider_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.delete("/{provider_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_service_provider(
    provider_id: int,
    current_user: dict = Depends(require_roles("admin"))
):
    await connect_db()
    tickets = await execute_query(
        "SELECT 1 FROM travel_tickets WHERE transport_company_id = %s LIMIT 1",
        (provider_id,),
        fetch_one=True
    )
    if tickets:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete provider with existing tickets"
        )

    affected = await execute_query(
        "DELETE FROM service_providers WHERE id = %s",
        (provider_id,),
        commit=True
    )
    await close_db()
    if not affected:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service provider not found"
        )

@router.patch("/{provider_id}/status", status_code=status.HTTP_200_OK)
async def update_provider_status(
    provider_id: int,
    status: bool,
    current_user: dict = Depends(require_roles("admin"))
):
    await connect_db()
    affected = await execute_query(
        "UPDATE service_providers SET status = %s WHERE id = %s",
        (status, provider_id),
        commit=True
    )
    if not affected:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service provider not found"
        )
    await close_db()
    return {"message": f"Service provider status set to {status}"}

@router.get("/{provider_id}/tickets", response_model=List[dict])
async def get_provider_tickets(
    provider_id: int,
    status: Optional[str] = None,
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    current_user: dict = Depends(get_current_user)
):
    await connect_db()
    query = """
    SELECT t.id, t.transport_type, t.departure_city, t.arrival_city,
           t.departure_time, t.arrival_time, t.price, t.currency,
           t.available_seats, t.total_seats, t.class_type, t.status
    FROM travel_tickets t
    WHERE t.transport_company_id = %s
    """
    params = [provider_id]
    
    if status:
        query += " AND t.status = %s"
        params.append(status)
    
    if from_date:
        query += " AND DATE(t.departure_time) >= %s"
        params.append(from_date)
    
    if to_date:
        query += " AND DATE(t.departure_time) <= %s"
        params.append(to_date)
    
    query += " ORDER BY t.departure_time DESC LIMIT %s OFFSET %s"
    params.extend([limit, skip])
    
    tickets = await execute_query(query, params, fetch_all=True)
    await close_db()
    return tickets