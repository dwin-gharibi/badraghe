from .base_seeder import BaseSeeder
from decorators.registry import get_faker, register_seeder
import random
from datetime import datetime, timedelta

@register_seeder('user_reservations', dependencies=['users', 'travel_tickets'])
class UserReservationSeeder(BaseSeeder):
    def seed(self, count=10):
        reservation_faker = get_faker('user_reservations')
        user_ids = self.get_random_ids('users', min(count, 10))
        ticket_ids = self.get_random_ids('travel_tickets', min(count, 20))
        
        if not user_ids or not ticket_ids:
            return 0

        data = []
        for _ in range(count):
            data.append(reservation_faker(self.fake, user_ids, ticket_ids))

        query = """
        INSERT INTO user_reservations (
            user_id, ticket_id, status, price_paid, refund_status
        ) VALUES (
            %(user_id)s, %(ticket_id)s, %(status)s, %(price_paid)s, %(refund_status)s
        )
        """
        
        inserted = self.execute_many(query, data)
        return inserted