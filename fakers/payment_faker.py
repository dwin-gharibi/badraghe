from faker import Faker
import random
import uuid
from decorators.registry import get_faker, register_faker

@register_faker('payments')
def fake_payment(fake=None, user_ids=None, reservation_ids=None, method_ids=None):
    
    statuses = ['successful', 'failed', 'pending']
    
    return {
        "user_id": random.choice(user_ids),
        "reservation_id": random.choice(reservation_ids),
        "amount": round(random.uniform(50, 1000), 2) * 10000000,
        "payment_method_id": random.choice(method_ids),
        "status": random.choice(statuses),
        "transaction_id": str(uuid.uuid4()),
        "currency": "IRR",
        "refund_amount": round(random.uniform(0, 200), 2) * 1000000,
        "payment_details": None
    }