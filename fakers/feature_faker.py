from faker import Faker
from decorators.registry import get_faker, register_faker

@register_faker('features')
def fake_feature(fake=None):
    
    return {
        "name": fake.unique.word().capitalize() + " feature",
        "description": fake.sentence()
    }