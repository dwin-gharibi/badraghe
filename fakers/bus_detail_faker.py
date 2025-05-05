from faker import Faker
import random
from decorators.registry import get_faker, register_faker

@register_faker('bus_details')
def fake_bus_detail(fake=None, ticket_ids=None):
    
    bus_types = ['VIP', 'standard', 'sleeper']
    seat_configs = ['1+2', '2+2']
    
    return {
        "ticket_id": random.choice(ticket_ids),
        "bus_company": fake.company(),
        "bus_type": random.choice(bus_types),
        "seats_per_row": random.choice(seat_configs)
    }