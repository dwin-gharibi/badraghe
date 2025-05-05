from faker import Faker
import random
from decorators.registry import get_faker, register_faker

@register_faker('reviews')
def fake_review(fake=None, user_ids=None, ticket_ids=None):
    
    return {
        "user_id": random.choice(user_ids),
        "ticket_id": random.choice(ticket_ids),
        "rating": random.randint(1, 5),
        "review_text": fake.paragraph()
    }