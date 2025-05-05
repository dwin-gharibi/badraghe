from faker import Faker
from decorators.registry import get_faker, register_faker

@register_faker('service_providers')
def fake_service_provider(fake=None):
    
    return {
        "name": fake.unique.company(),
        "contact_email": fake.company_email(),
        "contact_phone": f"+98{fake.msisdn()[3:]}",
        "address": fake.street_address(),
        "website_url": fake.url()
    }