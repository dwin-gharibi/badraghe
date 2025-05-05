from faker import Faker
import random
from decorators.registry import get_faker, register_faker

@register_faker('flight_details')
def fake_flight_detail(fake=None, ticket_ids=None):
    
    iranian_airlines = ["IranAir", "MahanAir", "QeshmAir", "CaspianAirlines", "ATAAirlines"]
    flight_classes = ['economy', 'business', 'first_class']
    
    iran_airports = [
        ("IKA", "Tehran Imam Khomeini"), 
        ("THR", "Tehran Mehrabad"),
        ("SYZ", "Shiraz"), 
        ("MHD", "Mashhad"), 
        ("TBZ", "Tabriz"), 
        ("AWZ", "Ahvaz"),
        ("KIH", "Kish Island")
    ]
    
    departure_code, _ = random.choice(iran_airports)
    arrival_code, _ = random.choice(iran_airports)
    while arrival_code == departure_code:
        arrival_code, _ = random.choice(iran_airports)

    return {
        "ticket_id": random.choice(ticket_ids),
        "airline_name": random.choice(iranian_airlines),
        "flight_class": random.choice(flight_classes),
        "stops": random.randint(0, 2),
        "flight_number": f"{random.choice(['IR', 'W5', 'QB', 'IV'])}{random.randint(100, 999)}",  # Iranian airline codes
        "departure_airport": departure_code,
        "arrival_airport": arrival_code
    }
