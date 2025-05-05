from .base_seeder import BaseSeeder
from decorators.registry import get_faker, register_seeder

@register_seeder('train_details', dependencies=['travel_tickets'])
class TrainDetailSeeder(BaseSeeder):
    def seed(self, count=10):
        train_faker = get_faker('train_details')
        ticket_ids = self.get_random_ids('travel_tickets', min(count, 20))
        
        if not ticket_ids:
            return 0

        data = []
        for ticket_id in ticket_ids[:count]:
            data.append(train_faker(self.fake, [ticket_id]))

        query = """
        INSERT INTO train_details (
            ticket_id, train_star_rating, private_cabin
        ) VALUES (
            %(ticket_id)s, %(train_star_rating)s, %(private_cabin)s
        )
        """
        
        inserted = self.execute_many(query, data)
        return inserted