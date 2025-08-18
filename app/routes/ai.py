from fastapi import FastAPI, HTTPException, Depends, Query
from app.db import connect_db, close_db, execute_query
from typing import List, Optional, Dict
from app.utils.llm_util import llm_helper
from fastapi.routing import APIRouter
from app.utils.auth_util import get_current_user
from app.routes.tickets import search_tickets, check_ticket_exists, TransportType, TicketClass, TicketStatus
from app.routes.reservations import create_reservation
from pydantic import BaseModel
import logging
import json
import re
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/ai")

class ReservationRequest(BaseModel):
    ticket_id: int
    user_id: int
    passengers: int

async def assist_user(task_description: str, context: Optional[str] = "") -> str:
    system = (
        "You are a helpful assistant for Badraghe, an online ticket reservation platform "
        "for plane, train, and bus travel. Guide the user in booking tickets, understanding "
        "trip options, and using platform features. Be polite and concise."
    )
    prompt = f"{context}\n\nUser task:\n{task_description}"
    response = await llm_helper(prompt=prompt, system=system)
    return response["content"]

async def explain_trips(trips_data: str, mode: str = "bus") -> str:
    system = (
        f"You are a travel assistant for Badraghe. Help the user understand available {mode} trips. "
        "The input is JSON data from the backend. Summarize it clearly, showing options with "
        "departure time, price (in IRR), duration, and company name. If no trips are found, "
        "return 'No {mode} trips found.'"
    )
    prompt = f"Here is the JSON data for {mode} trips:\n\n{trips_data}\n\nSummarize this for the user."
    response = await llm_helper(prompt=prompt, system=system)
    return response["content"]

async def recommend_tickets_helper(query: str, user_id: int) -> Dict:
    system = (
        "You are a data scientist for Badraghe, an online ticket reservation platform. "
        "Given a user query, search for available tickets using the provided search function. "
        "Summarize the results clearly, recommend the best option with a reason (e.g., cheapest, fastest), "
        "and if the user explicitly requests to book a ticket, call the create_reservation function with an available ticket."
    )
    tools = [
        {
            "type": "function",
            "function": {
                "name": "create_reservation",
                "description": "Create a reservation for a ticket",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "ticket_id": {"type": "integer", "description": "The ID of the ticket to reserve"},
                        "user_id": {"type": "integer", "description": "The ID of the user"},
                        "passengers": {"type": "integer", "description": "Number of passengers"}
                    },
                    "required": ["ticket_id", "user_id", "passengers"]
                }
            }
        }
    ]
    departure_city = None
    arrival_city = None
    transport_type = None
    travel_date = None
    query_lower = query.lower()
    if "from" in query_lower:
        match = re.search(r"from\s+([a-z\s]+)(?:\s+to|$)", query_lower)
        if match:
            departure_city = match.group(1).strip()
    if "to" in query_lower:
        match = re.search(r"to\s+([a-z\s]+)(?:\s|$)", query_lower)
        if match:
            arrival_city = match.group(1).strip()
    if any(word in query_lower for word in ["flight", "plane"]):
        transport_type = "plane"
    elif "train" in query_lower:
        transport_type = "train"
    elif "bus" in query_lower:
        transport_type = "bus"
    if "tomorrow" in query_lower:
        travel_date = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
    elif re.search(r"\b\d{4}-\d{2}-\d{2}\b", query):
        match = re.search(r"\b(\d{4}-\d{2}-\d{2})\b", query)
        travel_date = match.group(1)

    try:
        if transport_type:
            try:
                transport_type = TransportType(transport_type.lower())
            except ValueError:
                transport_type = None

        status_enum = TicketStatus.AVAILABLE
        if isinstance("available", str):
            status_enum = TicketStatus("available")

        tickets = await search_tickets(
            departure_city=departure_city,
            arrival_city=arrival_city,
            transport_type=transport_type,
            travel_date=travel_date,
            status=status_enum,
            limit=10
        )
    except Exception as e:
        logger.error(f"Search tickets error: {str(e)}")
        return {"recommendation": "No tickets found for your query.", "tickets": []}

    if not tickets:
        return {"recommendation": "No tickets found for your query.", "tickets": []}

    prompt = (
        f"User query: {query}\n\n"
        f"Available tickets:\n{json.dumps(tickets, default=str, indent=2)}\n\n"
        "Summarize the available tickets, highlighting departure time, price (in IRR), duration, and company name. "
        "Recommend the best option with a reason (e.g., cheapest, fastest). "
        "If the user explicitly requests to book a ticket (e.g., contains 'book' or 'reserve'), "
        "call the create_reservation function with the best ticket (lowest price)."
    )
    response = await llm_helper(prompt=prompt, system=system, tools=tools)
    logger.debug(response)

    if response.get("tool_calls"):
        for tool_call in response["tool_calls"]:
            if tool_call["function"]["name"] == "create_reservation":
                args = json.loads(tool_call["function"]["arguments"])
                ticket_id = args["ticket_id"]
                try:
                    ticket_exists = await check_ticket_exists(ticket_id)
                    if not ticket_exists:
                        logger.error(f"Ticket {ticket_id} not available or sold out")
                        return {
                            "recommendation": "Failed to book: Ticket not available or sold out",
                            "tickets": tickets
                        }
                    reservation = await create_reservation(ReservationRequest(**args))
                    return {
                        "recommendation": response["content"],
                        "tickets": tickets,
                        "reservation": reservation
                    }
                except Exception as e:
                    logger.error(f"Failed to create reservation: {str(e)}")
                    return {
                        "recommendation": f"Failed to book ticket: {str(e)}",
                        "tickets": tickets
                    }
    return {"recommendation": response["content"], "tickets": tickets}

@router.get("/assist")
async def get_ai_assistance(task: str = Query(..., description="Describe what you want help with")):
    try:
        result = await assist_user(task_description=task)
        return {"response": result}
    except Exception as e:
        logger.error(f"AI assistance error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/recommend")
async def recommend_trips(
    mode: str = Query("bus", enum=["bus", "train", "plane"]),
    from_city: Optional[str] = None,
    to_city: Optional[str] = None,
    travel_date: Optional[str] = None
):
    try:
        tickets = await search_tickets(
            departure_city=from_city,
            arrival_city=to_city,
            transport_type=mode,
            travel_date=travel_date,
            status="available",
            limit=10
        )
        if not tickets:
            return {"message": f"No {mode} trips found", "raw_data": []}
        summary = await explain_trips(trips_data=json.dumps(tickets, default=str), mode=mode)
        return {
            "summary": summary,
            "raw_data": tickets
        }
    except Exception as e:
        logger.error(f"Recommend trips error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/recommend-tickets")
async def recommend_tickets(
    query: str = Query(..., description="User query for ticket recommendations, e.g., 'Find me a cheap flight from Tehran to Shiraz for tomorrow'"),
    current_user: dict = Depends(get_current_user)
):
    try:
        result = await recommend_tickets_helper(query=query, user_id=current_user["user_id"])
        return result
    except Exception as e:
        logger.error(f"Recommend tickets error: {str(e)}")
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
        return {"summary": explanation["content"], "data": result}
    except Exception as e:
        logger.error(f"Train details error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await close_db()

@router.get("/bus-details")
async def explain_bus_details(ticket_id: int):
    try:
        await connect_db()
        query = "SELECT * FROM bus_details WHERE ticket_id = %s"
        result = await execute_query(query, (ticket_id,), fetch_one=True)
        if not result:
            raise HTTPException(status_code=404, detail="Bus details not found")
        explanation = await llm_helper(
            prompt=f"Explain these bus details to a user: {result}",
            system="You are a helpful assistant explaining bus-specific details."
        )
        return {"summary": explanation["content"], "data": result}
    except Exception as e:
        logger.error(f"Bus details error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await close_db()

@router.get("/flight-details")
async def explain_flight_details(ticket_id: int):
    try:
        await connect_db()
        query = "SELECT * FROM flight_details WHERE ticket_id = %s"
        result = await execute_query(query, (ticket_id,), fetch_one=True)
        if not result:
            raise HTTPException(status_code=404, detail="Flight details not found")
        explanation = await llm_helper(
            prompt=f"Explain these flight details to a user: {result}",
            system="You are a helpful assistant explaining flight-specific details."
        )
        return {"summary": explanation["content"], "data": result}
    except Exception as e:
        logger.error(f"Flight details error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await close_db()

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
        return {"summary": explanation["content"], "features": result}
    except Exception as e:
        logger.error(f"Bus features error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await close_db()