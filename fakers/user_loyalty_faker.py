from faker import Faker
import random

def fake_user_loyalty(fake=None, user_ids=None):
    if not fake:
        fake = Faker()
    
    return {
        "user_id": random.choice(user_ids),
        "total_points": random.randint(0, 10000)
    }