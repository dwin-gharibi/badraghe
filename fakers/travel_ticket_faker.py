from faker import Faker
import random
from datetime import datetime, timedelta

def fake_travel_ticket(fake=None, provider_ids=None):
    if not fake:
        fake = Faker()
    
    transport_types = ['plane', 'train', 'bus']
    class_types = ['economy', 'business', 'first']
    statuses = ['available', 'sold_out', 'canceled']
    
    departure_time = fake.future_datetime(end_date="+30d")
    arrival_time = departure_time + timedelta(hours=random.randint(1, 12))
    
    return {
        "transport_type": random.choice(transport_types),
        "departure_city": fake.city(),
        "arrival_city": fake.city(),
        "departure_time": departure_time.isoformat(),
        "arrival_time": arrival_time.isoformat(),
        "price": round(random.uniform(50, 1000), 2),
        "currency": "IRR",
        "available_seats": random.randint(0, 100),
        "total_seats": random.randint(50, 100),
        "transport_company_id": random.choice(provider_ids) if provider_ids else None,
        "class_type": random.choice(class_types),
        "status": random.choice(statuses)
    }