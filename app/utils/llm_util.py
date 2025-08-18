import httpx
import os
from app.config import settings
from typing import List, Optional, Dict
from pydantic import BaseModel
from fastapi import HTTPException
import json
import logging
from app.routes.tickets import search_tickets, check_ticket_exists
from app.routes.reservations import create_reservation

logger = logging.getLogger(__name__)

class ReservationRequest(BaseModel):
    ticket_id: int
    user_id: int
    passengers: int

async def llm_helper(prompt: str, system: str = "You are a helpful assistant.", tools: Optional[List[Dict]] = None) -> Dict:
    url = f"{settings.liara_base_url}/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {settings.liara_api_key}"
    }
    payload = {
        "model": "openai/gpt-4o-mini",
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": prompt}
        ]
    }
    if tools:
        payload["tools"] = tools
        payload["tool_choice"] = "auto"
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]
    except httpx.HTTPError as e:
        logger.error(f"Liara API error {e.response.status_code}: {e.response.text}")
        raise HTTPException(status_code=500, detail=f"Error from Liara API: {str(e)}")

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
        "The input is data from the backend, possibly JSON or tabular. Summarize it clearly, showing "
        "options with departure time, price, duration, and company name."
    )
    prompt = f"Here is the raw data for {mode} trips:\n\n{trips_data}\n\nSummarize this for the user."
    response = await llm_helper(prompt=prompt, system=system)
    return response["content"]

async def recommend_tickets_helper(query: str, user_id: int) -> Dict:
    system = (
        "You are a data scientist for Badraghe, an online ticket reservation platform. "
        "Given a user query, search for available tickets using the provided search function. "
        "Summarize the results clearly, recommend the best option with a reason, and if the user "
        "explicitly requests to book a ticket, call the create_reservation function with an available ticket."
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
    if "from" in query.lower():
        departure_city = query.lower().split("from")[1].split("to")[0].strip() if "to" in query.lower() else query.lower().split("from")[1].strip()
    if "to" in query.lower():
        arrival_city = query.lower().split("to")[1].strip().split(" ")[0]
    if "flight" in query.lower() or "plane" in query.lower():
        transport_type = "plane"
    elif "train" in query.lower():
        transport_type = "train"
    elif "bus" in query.lower():
        transport_type = "bus"

    try:
        tickets = await search_tickets({
            "departure_city": departure_city,
            "arrival_city": arrival_city,
            "transport_type": transport_type,
            "status": "available",
            "limit": 10
        })
    except Exception as e:
        logger.error(f"Search tickets error: {str(e)}")
        return {"recommendation": "No tickets found for your query.", "tickets": []}

    if not tickets:
        return {"recommendation": "No tickets found for your query.", "tickets": []}

    prompt = (
        f"User query: {query}\n\n"
        f"Available tickets:\n{json.dumps(tickets, indent=2)}\n\n"
        "Summarize the available tickets, highlighting departure time, price, duration, and company name. "
        "Recommend the best option with a reason (e.g., cheapest, fastest). "
        "If the user explicitly requests to book a ticket, call the create_reservation function with the best ticket."
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
                        raise HTTPException(status_code=404, detail="Ticket not available or sold out")
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