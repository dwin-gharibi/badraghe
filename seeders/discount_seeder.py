from .base_seeder import BaseSeeder
from decorators.registry import get_faker, register_seeder
from datetime import datetime, timedelta

@register_seeder('discounts')
class DiscountSeeder(BaseSeeder):
    def seed(self, count=10):
        discount_faker = get_faker('discounts')
        discounts_data = [discount_faker(self.fake) for _ in range(count)]
        
        insert_query = """
        INSERT INTO discounts (
            code, discount_type, discount_value, valid_from, valid_until, status
        ) VALUES (
            %(code)s, %(discount_type)s, %(discount_value)s, 
            %(valid_from)s, %(valid_until)s, %(status)s
        )
        """
        
        inserted_count = self.execute_many(insert_query, discounts_data)
        return inserted_count