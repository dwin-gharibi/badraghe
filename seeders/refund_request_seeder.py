from .base_seeder import BaseSeeder
from decorators.registry import get_faker, register_seeder

@register_seeder('refund_requests', dependencies=['users', 'payments'])
class RefundRequestSeeder(BaseSeeder):
    def seed(self, count=10):
        refund_faker = get_faker('refund_requests')
        user_ids = self.get_random_ids('users', min(count, 10))
        payment_ids = self.get_random_ids('payments', min(count, 20))
        
        if not user_ids or not payment_ids:
            return 0

        data = []
        for _ in range(count):
            data.append(refund_faker(self.fake, user_ids, payment_ids))

        query = """
        INSERT INTO refund_requests (
            user_id, payment_id, reason, status, refund_amount, processed_at
        ) VALUES (
            %(user_id)s, %(payment_id)s, %(reason)s, %(status)s, 
            %(refund_amount)s, %(processed_at)s
        )
        """
        
        inserted = self.execute_many(query, data)

        return inserted