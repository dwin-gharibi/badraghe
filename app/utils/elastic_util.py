from elasticsearch import Elasticsearch, exceptions
from app.config import settings

es = Elasticsearch(
    settings.elasticsearch_url,
    basic_auth=(settings.elasticsearch_user, settings.elasticsearch_password),
    verify_certs=False,
    headers={
        "Accept": "application/vnd.elasticsearch+json; compatible-with=7",
        "Content-Type": "application/vnd.elasticsearch+json; compatible-with=7"
    }
)

async def index_ticket(ticket: dict):
    try:
        es.index(
            index="tickets",
            id=ticket["id"],
            body={
                "id": ticket["id"],
                "transport_type": ticket["transport_type"],
                "departure_city": ticket["departure_city"],
                "arrival_city": ticket["arrival_city"],
                "departure_time": ticket["departure_time"],
                "arrival_time": ticket["arrival_time"],
                "price": ticket["price"],
                "currency": ticket["currency"],
                "available_seats": ticket["available_seats"],
                "total_seats": ticket["total_seats"],
                "transport_company_id": ticket["transport_company_id"],
                "class_type": ticket["class_type"],
                "status": ticket["status"],
                "company_name": ticket.get("company_name"),
                "details": ticket.get("details"),
                "features": ticket.get("features"),
            }
        )
    except Exception as e:
        raise Exception(f"Failed to index ticket: {str(e)}")

async def delete_ticket_index(ticket_id: int):
    try:
        es.delete(index="tickets", id=ticket_id)
    except exceptions.NotFoundError:
        pass
    except Exception as e:
        raise Exception(f"Failed to delete ticket from Elasticsearch: {str(e)}")

async def search_tickets_es(params: dict) -> list:
    try:
        query = {
            "bool": {
                "filter": [
                    {"term": {"status": "available"}}
                ],
                "must": []
            }
        }
        if params.get("departure_city"):
            query["bool"]["must"].append({"match": {"departure_city": params["departure_city"]}})
        if params.get("arrival_city"):
            query["bool"]["must"].append({"match": {"arrival_city": params["arrival_city"]}})
        if params.get("travel_date"):
            query["bool"]["must"].append({"match": {"departure_time": params["travel_date"]}})
        if params.get("transport_type"):
            query["bool"]["must"].append({"term": {"transport_type": params["transport_type"]}})
        if params.get("price_min"):
            query["bool"]["filter"].append({"range": {"price": {"gte": params["price_min"]}}})
        if params.get("price_max"):
            query["bool"]["filter"].append({"range": {"price": {"lte": params["price_max"]}}})
        if params.get("company_name"):
            query["bool"]["must"].append({"match": {"company_name": params["company_name"]}})
        if params.get("departure_time"):
            query["bool"]["filter"].append({"range": {"departure_time": {"gte": params["departure_time"]}}})
        if params.get("class_type"):
            query["bool"]["must"].append({"term": {"class_type": params["class_type"]}})

        response = es.search(
            index="tickets",
            body={
                "query": query,
                "sort": [{"departure_time": {"order": "asc"}}],
                "from": params.get("skip", 0),
                "size": params.get("limit", 100),
            }
        )
        return [hit["_source"] for hit in response["hits"]["hits"]], response["hits"]["total"]["value"]
    except Exception as e:
        raise Exception(f"Elasticsearch search failed: {str(e)}")