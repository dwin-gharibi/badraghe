from faker import Faker
import random
from datetime import datetime, timedelta

def fake_reservation(fake=None, user_ids=None, ticket_ids=None):
    if not fake:
        fake = Faker()
    
    statuses = ['temporary', 'reserved', 'paid', 'canceled']
    refund_statuses = ['not_requested', 'pending', 'approved', 'denied']
    
    return {
        "user_id": random.choice(user_ids),
        "ticket_id": random.choice(ticket_ids),
        "status": random.choice(statuses),
        "price_paid": round(random.uniform(50, 1000), 2),
        "refund_status": random.choice(refund_statuses)
    }