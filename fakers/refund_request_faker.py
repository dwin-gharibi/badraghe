from faker import Faker
import random
from datetime import datetime, timedelta
from decorators.registry import get_faker, register_faker

@register_faker('refund_requests')
def fake_refund_request(fake=None, user_ids=None, payment_ids=None):
    
    statuses = ['pending', 'approved', 'rejected']
    reasons = [
        "Change of plans",
        "Found better price",
        "Service not as described",
        "Double booking",
        "Other reasons"
    ]
    
    return {
        "user_id": random.choice(user_ids),
        "payment_id": random.choice(payment_ids),
        "reason": random.choice(reasons),
        "status": random.choice(statuses),
        "refund_amount": round(random.uniform(50, 500), 2),
        "processed_at": fake.date_time_this_month() if random.choice([True, False]) else None
    }