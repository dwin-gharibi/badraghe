from faker import Faker
import random

def fake_report(fake=None, user_ids=None, ticket_ids=None):
    if not fake:
        fake = Faker()
    
    categories = ['payment_issue', 'delay', 'cancellation', 'other']
    statuses = ['pending', 'reviewed', 'resolved']
    
    return {
        "user_id": random.choice(user_ids),
        "ticket_id": random.choice(ticket_ids) if random.choice([True, False]) else None,
        "category": random.choice(categories),
        "message": fake.paragraph(),
        "status": random.choice(statuses),
        "resolution": fake.paragraph() if random.choice([True, False]) else None,
        "assigned_to": random.choice(user_ids) if random.choice([True, False]) else None
    }