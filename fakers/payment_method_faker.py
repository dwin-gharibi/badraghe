from faker import Faker
import random
from decorators.registry import get_faker, register_faker

@register_faker('payment_methods')
def fake_payment_method(fake=None):
    
    methods = ['CreditCard', 'ZarinPal', 'BankTransfer', 'IDPay', 'DigiPay', 'Cryptocurrency']
    
    return {
        "name": random.choice(methods),
        "description": fake.sentence(),
        "is_active": random.choice([True, False])
    }