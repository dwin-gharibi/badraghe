from faker import Faker
import random
from datetime import datetime, timedelta

def fake_notification(fake=None, user_ids=None):
    if not fake:
        fake = Faker()
    
    types = ['system', 'user', 'transaction', 'other']
    statuses = ['sent', 'pending', 'failed']
    
    return {
        "user_id": random.choice(user_ids),
        "message": fake.sentence(),
        "status": random.choice(statuses),
        "notification_type": random.choice(types),
        "is_read": random.choice([True, False]),
        "sent_at": fake.date_time_this_month() if random.choice([True, False]) else None
    }