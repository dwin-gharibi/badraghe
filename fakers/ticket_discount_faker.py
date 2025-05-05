from faker import Faker
import random

def fake_ticket_discount(fake=None, ticket_ids=None, discount_ids=None):
    if not fake:
        fake = Faker()
    
    return {
        "ticket_id": random.choice(ticket_ids),
        "discount_id": random.choice(discount_ids)
    }