from faker import Faker
import random
from decorators.registry import get_faker, register_faker

@register_faker('support_conversations')
def fake_support_conversation(fake=None, ticket_ids=None, user_ids=None):

    return {
        "ticket_id": random.choice(ticket_ids),
        "user_id": random.choice(user_ids),
        "message": fake.paragraph(),
        "message_type": random.choice(["user", "bot"])
    }