from .base_seeder import BaseSeeder
from decorators.registry import get_faker, register_seeder

@register_seeder('service_providers')
class ServiceProviderSeeder(BaseSeeder):
    def seed(self, count=10):
        provider_faker = get_faker('service_providers')
        providers_data = [provider_faker(self.fake) for _ in range(count)]
        
        insert_query = """
        INSERT INTO service_providers (
            name, contact_email, contact_phone, address, website_url
        ) VALUES (
            %(name)s, %(contact_email)s, %(contact_phone)s, %(address)s, %(website_url)s
        )
        """
        
        inserted_count = self.execute_many(insert_query, providers_data)
        return inserted_count