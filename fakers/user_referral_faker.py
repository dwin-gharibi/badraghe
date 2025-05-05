from faker import Faker
import random

def fake_user_referral(fake=None, user_ids=None):
    if not fake:
        fake = Faker()
    
    referrer = random.choice(user_ids)
    referred = random.choice([uid for uid in user_ids if uid != referrer])
    
    return {
        "referrer_id": referrer,
        "referred_id": referred
    }