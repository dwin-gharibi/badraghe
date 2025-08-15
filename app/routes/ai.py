from fastapi import FastAPI, HTTPException, Depends, Query
from app.db import connect_db, close_db, execute_query
from typing import List, Optional
from app.utils.llm_util import assist_user, explain_trips, llm_helper
from fastapi.routing import APIRouter

router = APIRouter(prefix="/ai")

@router.get("/assist")
async def get_ai_assistance(task: str = Query(..., description="Describe what you want help with")):
    try:
        result = await assist_user(task_description=task)
        return {"response": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/recommend")
async def recommend_trips(
    mode: str = Query("bus", enum=["bus", "train", "plane"]),
    from_city: Optional[str] = None,
    to_city: Optional[str] = None,
):
    try:
        await connect_db()
        query = """
        SELECT * FROM travel_tickets
        WHERE departure_city = %s OR arrival_city = %s AND transport_type = %s
        ORDER BY departure_time ASC
        """
        trips = await execute_query(
            query,
            (from_city, to_city, mode),
            fetch_all=True
        )

        if not trips:
            return {"message": "No trips found"}

        summary = await explain_trips(trips_data=str(trips), mode=mode)
        return {
            "summary": summary,
            "raw_data": trips
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/recommend-tickets")
async def recommend_tickets(
        from_city: Optional[str] = Query(None, description="Departure city"),
        to_city: Optional[str] = Query(None, description="Arrival city"),
        user_pref: Optional[str] = Query("", description="Describe your preferences or what you want advice on")
):
    if not from_city and not to_city:
        raise HTTPException(status_code=400, detail="At least one of from_city or to_city must be specified")

    try:
        await connect_db()

        query = """
        SELECT * FROM travel_tickets
        WHERE (%s IS NULL OR departure_city = %s)
          AND (%s IS NULL OR arrival_city = %s)
        ORDER BY departure_time ASC
        """
        params = (from_city, from_city, to_city, to_city)

        tickets = await execute_query(
            query,
            params,
            fetch_all=True
        )

        if not tickets:
            return {"message": "No tickets found matching your criteria."}

        tickets_str = str(tickets)
        prompt = (
            f"Given the following list of travel tickets:\n{tickets_str}\n\n"
            f"The user preferences are: {user_pref or 'No specific preferences'}.\n"
            "Please recommend the best tickets based on these preferences and explain why."
        )

        explanation = await assist_user(task_description=prompt)

        await close_db()

        return {
            "recommendation": explanation,
            "tickets": tickets
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/train-details")
async def explain_train_details(ticket_id: int):
    try:
        await connect_db()
        query = "SELECT * FROM train_details WHERE ticket_id = %s"
        result = await execute_query(query, (ticket_id,), fetch_one=True)

        if not result:
            raise HTTPException(status_code=404, detail="Train details not found")

        explanation = await llm_helper(
            prompt=f"Explain these train details to a user: {result}",
            system="You are a helpful assistant explaining train-specific details."
        )
        return {"summary": explanation, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/bus-details")
async def explain_train_details(ticket_id: int):
    try:
        await connect_db()
        query = "SELECT * FROM bus_details WHERE ticket_id = %s"
        result = await execute_query(query, (ticket_id,), fetch_one=True)

        if not result:
            raise HTTPException(status_code=404, detail="Bus details not found")

        explanation = await llm_helper(
            prompt=f"Explain these Bus details to a user: {result}",
            system="You are a helpful assistant explaining train-specific details."
        )
        return {"summary": explanation, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/flight-details")
async def explain_train_details(ticket_id: int):
    try:
        await connect_db()
        query = "SELECT * FROM flight_details WHERE ticket_id = %s"
        result = await execute_query(query, (ticket_id,), fetch_one=True)

        if not result:
            raise HTTPException(status_code=404, detail="Flight details not found")

        explanation = await llm_helper(
            prompt=f"Explain these flight details to a user: {result}",
            system="You are a helpful assistant explaining train-specific details."
        )
        return {"summary": explanation, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/bus-features")
async def explain_bus_features(ticket_id: int):
    try:
        await connect_db()
        query = """
        SELECT bf.* FROM bus_features bf
        JOIN bus_details bd ON bf.bus_id = bd.id
        WHERE bd.ticket_id = %s
        """
        result = await execute_query(query, (ticket_id,), fetch_all=True)

        if not result:
            raise HTTPException(status_code=404, detail="Bus features not found")

        explanation = await llm_helper(
            prompt=f"Summarize the bus features from this data: {result}",
            system="You are a helpful assistant explaining bus trip amenities."
        )
        return {"summary": explanation, "features": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

