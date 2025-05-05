from faker import Faker
import random
from decorators.registry import get_faker, register_faker

@register_faker('user_discounts')
def fake_user_discount(fake=None, user_ids=None, discount_ids=None, payment_ids=None):
    
    return {
        "user_id": random.choice(user_ids),
        "discount_id": random.choice(discount_ids),
        "payment_id": random.choice(payment_ids)
    }