from .base_seeder import BaseSeeder
from decorators.registry import get_faker, register_seeder

@register_seeder('user_discounts', dependencies=['users', 'discounts', 'payments'])
class UserDiscountSeeder(BaseSeeder):
    def seed(self, count=10):
        user_discount_faker = get_faker('user_discounts')
        user_ids = self.get_random_ids('users', min(count, 10))
        discount_ids = self.get_random_ids('discounts', min(count, 5))
        payment_ids = self.get_random_ids('payments', min(count, 20))
        
        if not user_ids or not discount_ids or not payment_ids:
            return 0

        data = []
        for _ in range(count):
            data.append(user_discount_faker(self.fake, user_ids, discount_ids, payment_ids))

        query = """
        INSERT INTO user_discounts (
            user_id, discount_id, payment_id
        ) VALUES (
            %(user_id)s, %(discount_id)s, %(payment_id)s
        )
        """
        
        inserted = self.execute_many(query, data)
        return inserted