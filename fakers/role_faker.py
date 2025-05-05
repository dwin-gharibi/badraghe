from faker import Faker
import random
from decorators.registry import get_faker, register_faker

@register_faker('roles')
def fake_role(fake=None):
    
    return {
        "name": fake.unique.job(),
        "description": fake.text(max_nb_chars=100),
        "parent_role_id": None,
        "status": random.choice([True, False])
    }