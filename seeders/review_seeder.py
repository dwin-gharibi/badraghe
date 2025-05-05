from .base_seeder import BaseSeeder
from decorators.registry import get_faker, register_seeder

@register_seeder('reviews', dependencies=['users', 'travel_tickets'])
class ReviewSeeder(BaseSeeder):
    def seed(self, count=10):
        review_faker = get_faker('reviews')
        user_ids = self.get_random_ids('users', min(count, 10))
        ticket_ids = self.get_random_ids('travel_tickets', min(count, 20))
        
        if not user_ids or not ticket_ids:
            return 0

        data = []
        for _ in range(count):
            data.append(review_faker(self.fake, user_ids, ticket_ids))

        query = """
        INSERT INTO reviews (
            user_id, ticket_id, rating, review_text
        ) VALUES (
            %(user_id)s, %(ticket_id)s, %(rating)s, %(review_text)s
        )
        """
        
        inserted = self.execute_many(query, data)
        return inserted