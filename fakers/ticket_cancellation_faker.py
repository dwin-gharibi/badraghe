from faker import Faker
import random

def fake_ticket_cancellation(fake=None, reservation_ids=None, user_ids=None):
    if not fake:
        fake = Faker()
    
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