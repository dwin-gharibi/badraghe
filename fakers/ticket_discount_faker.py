from faker import Faker
import random
from decorators.registry import get_faker, register_faker

@register_faker('ticket_discounts')
def fake_ticket_discount(fake=None, ticket_ids=None, discount_ids=None):
    
    return {
        "ticket_id": random.choice(ticket_ids),
        "discount_id": random.choice(discount_ids)
    }