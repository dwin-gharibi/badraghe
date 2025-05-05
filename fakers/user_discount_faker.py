from faker import Faker
import random

def fake_user_discount(fake=None, user_ids=None, discount_ids=None, payment_ids=None):
    if not fake:
        fake = Faker()
    
    return {
        "user_id": random.choice(user_ids),
        "discount_id": random.choice(discount_ids),
        "payment_id": random.choice(payment_ids)
    }