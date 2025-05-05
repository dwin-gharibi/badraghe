from faker import Faker
import random

def fake_support_category(fake=None):
    if not fake:
        fake = Faker()
    
    categories = [
        "Booking Issues",
        "Payment Problems",
        "Cancellation",
        "Refund Request",
        "Account Issues",
        "Technical Support",
        "Other Questions"
    ]
    
    return {
        "name": random.choice(categories),
        "description": fake.sentence()
    }