from faker import Faker
import random
from decorators.registry import get_faker, register_faker

@register_faker('train_details')
def fake_train_detail(fake=None, ticket_ids=None):
    
    return {
        "ticket_id": random.choice(ticket_ids),
        "train_star_rating": random.randint(1, 5),
        "private_cabin": random.choice([True, False])
    }