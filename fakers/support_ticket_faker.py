from faker import Faker
import random
from decorators.registry import get_faker, register_faker

@register_faker('support_tickets')
def fake_support_ticket(fake=None, user_ids=None, category_ids=None):
    
    statuses = ['open', 'in_progress', 'resolved', 'closed']
    priorities = ['low', 'medium', 'high']
    
    return {
        "user_id": random.choice(user_ids),
        "category_id": random.choice(category_ids),
        "subject": fake.sentence(),
        "description": fake.paragraph(),
        "status": random.choice(statuses),
        "priority": random.choice(priorities)
    }