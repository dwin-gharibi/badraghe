from .base_seeder import BaseSeeder
from decorators.registry import get_faker, register_seeder

@register_seeder('user_loyalty', dependencies=['users'])
class UserLoyaltySeeder(BaseSeeder):
    def seed(self, count=10):
        loyalty_faker = get_faker('user_loyalty')
        user_ids = self.get_random_ids('users', min(count, 10))
        
        if not user_ids:
            return 0

        data = []
        for user_id in user_ids[:count]:
            data.append(loyalty_faker(self.fake, [user_id]))

        query = """
        INSERT INTO user_loyalty (
            user_id, total_points
        ) VALUES (
            %(user_id)s, %(total_points)s
        )
        """
        
        inserted = self.execute_many(query, data)
        return inserted