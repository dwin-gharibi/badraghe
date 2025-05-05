from faker import Faker
import random
from datetime import datetime, timedelta
from decorators.registry import get_faker, register_faker

@register_faker('notifications')
def fake_notification(fake=None, user_ids=None):

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