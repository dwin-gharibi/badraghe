from faker import Faker
import random

def fake_role(fake=None):
    if not fake:
        fake = Faker()
    
    return {
        "name": fake.unique.job(),
        "description": fake.text(max_nb_chars=100),
        "parent_role_id": None,
        "status": random.choice([True, False])
    }