from faker import Faker
import random

def fake_permission(fake=None):
    if not fake:
        fake = Faker()
    
    permission_types = ['create', 'read', 'update', 'delete']
    
    return {
        "name": fake.unique.word().capitalize() + " permission",
        "description": fake.sentence(),
        "type": random.choice(permission_types),
        "status": random.choice([True, False])
    }