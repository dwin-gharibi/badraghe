from .base_seeder import BaseSeeder
from decorators.registry import get_faker, register_seeder

@register_seeder('support_tickets', dependencies=['users', 'support_categories'])
class SupportTicketSeeder(BaseSeeder):
    def seed(self, count=10):
        ticket_faker = get_faker('support_tickets')
        user_ids = self.get_random_ids('users', min(count, 10))
        category_ids = self.get_random_ids('support_categories', min(count, 5))
        
        if not user_ids or not category_ids:
            return 0

        data = []
        for _ in range(count):
            data.append(ticket_faker(self.fake, user_ids, category_ids))

        query = """
        INSERT INTO support_tickets (
            user_id, category_id, subject, description, status, priority
        ) VALUES (
            %(user_id)s, %(category_id)s, %(subject)s, %(description)s,
            %(status)s, %(priority)s
        )
        """
        
        inserted = self.execute_many(query, data)
        return inserted