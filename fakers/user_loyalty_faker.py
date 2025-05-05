from faker import Faker
import random
from decorators.registry import get_faker, register_faker

@register_faker('user_loyalty')
def fake_user_loyalty(fake=None, user_ids=None):
    
    return {
        "user_id": random.choice(user_ids),
        "total_points": random.randint(0, 10000)
    }