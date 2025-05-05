from faker import Faker
import random
from decorators.registry import get_faker, register_faker

@register_faker('support_categories')
def fake_support_category(fake=None):
    
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