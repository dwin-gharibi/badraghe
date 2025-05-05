from faker import Faker

def fake_service_provider(fake=None):
    if not fake:
        fake = Faker()
    
    return {
        "name": fake.unique.company(),
        "contact_email": fake.company_email(),
        "contact_phone": f"+98{fake.msisdn()[3:]}",
        "address": fake.street_address(),
        "website_url": fake.url()
    }