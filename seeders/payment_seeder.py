from .base_seeder import BaseSeeder
from decorators.registry import get_faker, register_seeder

@register_seeder('payments', dependencies=['users', 'user_reservations', 'payment_methods'])
class PaymentSeeder(BaseSeeder):
    def seed(self, count=10):
        payment_faker = get_faker('payments')
        user_ids = self.get_random_ids('users', min(count, 10))
        reservation_ids = self.get_random_ids('user_reservations', min(count, 20))
        method_ids = self.get_random_ids('payment_methods', min(count, 5))
        
        if not user_ids or not reservation_ids or not method_ids:
            return 0

        data = []
        for _ in range(count):
            data.append(payment_faker(self.fake, user_ids, reservation_ids, method_ids))

        query = """
        INSERT INTO payments (
            user_id, reservation_id, amount, payment_method_id, status,
            transaction_id, currency, refund_amount, payment_details
        ) VALUES (
            %(user_id)s, %(reservation_id)s, %(amount)s, %(payment_method_id)s, %(status)s,
            %(transaction_id)s, %(currency)s, %(refund_amount)s, %(payment_details)s
        )
        """
        
        inserted = self.execute_many(query, data)
        
        for payment in data:
            self.execute_query(
                "UPDATE user_reservations SET payment_id = %s WHERE id = %s",
                (payment['id'], payment['reservation_id'])
            )
        
        return inserted