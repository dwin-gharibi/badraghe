from faker import Faker
import random

def fake_train_detail(fake=None, ticket_ids=None):
    if not fake:
        fake = Faker()
    
    return {
        "ticket_id": random.choice(ticket_ids),
        "train_star_rating": random.randint(1, 5),
        "private_cabin": random.choice([True, False])
    }