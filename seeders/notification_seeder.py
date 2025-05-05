from .base_seeder import BaseSeeder
from decorators.registry import get_faker, register_seeder

@register_seeder('notifications', dependencies=['users'])
class NotificationSeeder(BaseSeeder):
    def seed(self, count=10):
        notification_faker = get_faker('notifications')
        user_ids = self.get_random_ids('users', min(count, 10))
        
        if not user_ids:
            return 0

        data = []
        for _ in range(count):
            data.append(notification_faker(self.fake, user_ids))

        query = """
        INSERT INTO notifications (
            user_id, message, status, sent_at, notification_type, is_read
        ) VALUES (
            %(user_id)s, %(message)s, %(status)s, %(sent_at)s, 
            %(notification_type)s, %(is_read)s
        )
        """
        
        inserted = self.execute_many(query, data)
        return inserted