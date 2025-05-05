from faker import Faker

def fake_feature(fake=None):
    if not fake:
        fake = Faker()
    
    return {
        "name": fake.unique.word().capitalize() + " feature",
        "description": fake.sentence()
    }