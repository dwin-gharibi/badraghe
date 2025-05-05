from faker import Faker
import random
import json
from datetime import datetime, timedelta

def fake_user(fake=None):
    if not fake:
        fake = Faker()
    
    return {
        "first_name": fake.first_name(),
        "last_name": fake.last_name(),
        "email": fake.unique.email(),
        "phone": f"+98{random.randint(200, 999)}{random.randint(200, 999)}{random.randint(1000, 9999)}",
        "password": fake.password(length=12, special_chars=True, digits=True, upper_case=True, lower_case=True),
        "country": fake.country(),
        "state": fake.state(),
        "city": fake.city(),
        "address": fake.street_address(),
        "zip_code": fake.zipcode(),
        "date_of_birth": fake.date_of_birth(minimum_age=18, maximum_age=70).isoformat(),
        "gender": random.choice(["male", "female", "other"]),
        "profile_picture_url": f"https://example.com/profiles/{fake.uuid4()}.jpg",
        "status": random.choice([True, False]),
        "is_verified": random.choice([True, False]),
        "bio": fake.text(max_nb_chars=200),
        "preferences": json.dumps({
            "theme": random.choice(["light", "dark"]),
            "language": random.choice(["fa", "en", "ar"]),
            "notifications": random.choice([True, False])
        }),
        "last_login": fake.date_time_this_year().isoformat() if random.choice([True, False]) else None
    }