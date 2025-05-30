from fastapi import APIRouter, Query
from typing import Optional
from app.db import execute_query, connect_db, close_db

router = APIRouter(prefix="/cities")

@router.get("/", summary="Get all unique cities")
async def get_cities():
    await connect_db()
    query = """
    SELECT DISTINCT city_name FROM (
        SELECT departure_city AS city_name FROM travel_tickets
        UNION
        SELECT arrival_city FROM travel_tickets
    ) AS cities
    ORDER BY city_name;
    """
    cities = await execute_query(query, fetch_all=True)
    city_list = [c["city_name"] for c in cities]
    await close_db()
    return {"cities": city_list}

@router.get("/departure", summary="Search departure cities")
async def search_departure_cities(q: Optional[str] = Query(None, description="Search term for departure city")):
    await connect_db()
    if q:
        query = """
        SELECT DISTINCT departure_city AS city_name
        FROM travel_tickets
        WHERE departure_city LIKE %(search_term)s
        ORDER BY city_name;
        """
        params = {"search_term": f"%{q}%"}
    else:
        query = """
        SELECT DISTINCT departure_city AS city_name
        FROM travel_tickets
        ORDER BY city_name;
        """
        params = {}
    
    cities = await execute_query(query, params, fetch_all=True)
    city_list = [c["city_name"] for c in cities]
    await close_db()
    return {"departure_cities": city_list}

@router.get("/arrival", summary="Search arrival cities")
async def search_arrival_cities(q: Optional[str] = Query(None, description="Search term for arrival city")):
    await connect_db()
    if q:
        query = """
        SELECT DISTINCT arrival_city AS city_name
        FROM travel_tickets
        WHERE arrival_city LIKE %(search_term)s
        ORDER BY city_name;
        """
        params = {"search_term": f"%{q}%"}
    else:
        query = """
        SELECT DISTINCT arrival_city AS city_name
        FROM travel_tickets
        ORDER BY city_name;
        """
        params = {}

    cities = await execute_query(query, params, fetch_all=True)
    city_list = [c["city_name"] for c in cities]
    await close_db()
    return {"arrival_cities": city_list}
