from faker import Faker
import random
from decorators.registry import get_faker, register_faker

@register_faker('ticket_cancellations')
def fake_ticket_cancellation(fake=None, reservation_ids=None, user_ids=None):

    reasons = [
        "change_of_plans",
        "price_issue",
        "delay",
        "duplicate_booking",
        "other"
    ]
    
    return {
        "reservation_id": random.choice(reservation_ids),
        "canceled_by": random.choice(user_ids),
        "cancellation_reason": fake.paragraph(),
        "cancellation_choice": random.choice(reasons)
    }