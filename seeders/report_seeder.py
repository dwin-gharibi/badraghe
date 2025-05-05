from .base_seeder import BaseSeeder
from decorators.registry import get_faker, register_seeder

@register_seeder('reports', dependencies=['users', 'travel_tickets'])
class ReportSeeder(BaseSeeder):
    def seed(self, count=10):
        report_faker = get_faker('reports')
        
        user_ids = self.get_random_ids('users', min(count, 10))
        ticket_ids = self.get_random_ids('travel_tickets', min(count, 20))
        
        if not user_ids:
            return 0

        data = []
        for _ in range(count):
            data.append(report_faker(self.fake, user_ids, ticket_ids))

        query = """
        INSERT INTO reports (
            user_id, ticket_id, category, message, status, resolution, assigned_to
        ) VALUES (
            %(user_id)s, %(ticket_id)s, %(category)s, %(message)s, 
            %(status)s, %(resolution)s, %(assigned_to)s
        )
        """
        
        inserted = self.execute_many(query, data)
        return inserted