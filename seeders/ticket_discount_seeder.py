from .base_seeder import BaseSeeder
from decorators.registry import get_faker, register_seeder

@register_seeder('ticket_discounts', dependencies=['travel_tickets', 'discounts'])
class TicketDiscountSeeder(BaseSeeder):
    def seed(self, count=10):
        ticket_discount_faker = get_faker('ticket_discounts')
        ticket_ids = self.get_random_ids('travel_tickets', min(count, 20))
        discount_ids = self.get_random_ids('discounts', min(count, 5))
        
        if not ticket_ids or not discount_ids:
            return 0

        data = []
        for _ in range(count):
            data.append(ticket_discount_faker(self.fake, ticket_ids, discount_ids))

        query = """
        INSERT INTO ticket_discounts (
            ticket_id, discount_id
        ) VALUES (
            %(ticket_id)s, %(discount_id)s
        )
        """
        
        inserted = self.execute_many(query, data)
        return inserted