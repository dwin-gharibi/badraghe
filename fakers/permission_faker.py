from faker import Faker
import random
from decorators.registry import get_faker, register_faker

@register_faker('permissions')

def fake_permission(fake=None):
    
    permission_types = ['create', 'read', 'update', 'delete']
    
    return {
        "name": fake.unique.word().capitalize() + " permission",
        "description": fake.sentence(),
        "type": random.choice(permission_types),
        "status": random.choice([True, False])
    }