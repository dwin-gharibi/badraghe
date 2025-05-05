from .base_seeder import BaseSeeder
from decorators.registry import get_faker, register_seeder

@register_seeder('payment_methods')
class PaymentMethodSeeder(BaseSeeder):
    def seed(self, count=10):
        method_faker = get_faker('payment_methods')
        methods_data = [method_faker(self.fake) for _ in range(count)]
        
        insert_query = """
        INSERT INTO payment_methods (
            name, description, is_active
        ) VALUES (
            %(name)s, %(description)s, %(is_active)s
        )
        """
        
        inserted_count = self.execute_many(insert_query, methods_data)
        return inserted_count