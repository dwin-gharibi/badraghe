from .base_seeder import BaseSeeder
from decorators.registry import get_faker, register_seeder

@register_seeder('ticket_cancellations', dependencies=['user_reservations', 'users'])
class TicketCancellationSeeder(BaseSeeder):
    def seed(self, count=10):
        cancellation_faker = get_faker('ticket_cancellations')
        reservation_ids = self.get_random_ids('user_reservations', min(count, 20))
        user_ids = self.get_random_ids('users', min(count, 10))
        
        if not reservation_ids or not user_ids:
            return 0

        data = []
        for _ in range(count):
            data.append(cancellation_faker(self.fake, reservation_ids, user_ids))

        query = """
        INSERT INTO ticket_cancellations (
            reservation_id, canceled_by, cancellation_reason, cancellation_choice
        ) VALUES (
            %(reservation_id)s, %(canceled_by)s, %(cancellation_reason)s, %(cancellation_choice)s
        )
        """
        
        inserted = self.execute_many(query, data)
        return inserted