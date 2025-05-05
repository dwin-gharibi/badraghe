from faker import Faker
import random

def fake_payment_method(fake=None):
    if not fake:
        fake = Faker('en_US')
    
    methods = ['CreditCard', 'ZarinPal', 'BankTransfer', 'IDPay', 'DigiPay', 'Cryptocurrency']
    
    return {
        "name": random.choice(methods),
        "description": fake.sentence(),
        "is_active": random.choice([True, False])
    }