from faker import Faker
import random
from decorators.registry import get_faker, register_faker

@register_faker('user_referrals')
def fake_user_referral(fake=None, user_ids=None):
    
    referrer = random.choice(user_ids)
    referred = random.choice([uid for uid in user_ids if uid != referrer])
    
    return {
        "referrer_id": referrer,
        "referred_id": referred
    }