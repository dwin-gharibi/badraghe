from faker import Faker
import random
from datetime import datetime, timedelta
from decorators.registry import get_faker, register_faker

@register_faker('discounts')
def fake_discount(fake=None):
    
    discount_types = ['percentage', 'fixed']
    
    valid_from = fake.future_datetime(end_date="+30d")
    valid_until = valid_from + timedelta(days=random.randint(7, 90))
    
    return {
        "code": fake.unique.bothify(text="DISCOUNT-??-####").upper(),
        "discount_type": random.choice(discount_types),
        "discount_value": round(random.uniform(5, 50), 2),
        "valid_from": valid_from.isoformat(),
        "valid_until": valid_until.isoformat(),
        "status": random.choice([True, False])
    }