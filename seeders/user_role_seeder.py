from .base_seeder import BaseSeeder
from decorators.registry import get_faker, register_seeder
from datetime import datetime, timedelta
import random

@register_seeder('user_role', dependencies=['users', 'roles'])
class UserRoleSeeder(BaseSeeder):
    def seed(self, count=10):
        user_ids = self.get_random_ids('users', min(count, 10))
        role_ids = self.get_random_ids('roles', min(count, 5))
        
        if not user_ids or not role_ids:
            return 0

        data = []
        for user_id in user_ids:
            for role_id in role_ids[:count//len(user_ids)+1]:
                data.append({
                    "user_id": user_id,
                    "role_id": role_id,
                    "expired_at": (datetime.now() + timedelta(days=365)).isoformat() if random.random() > 0.7 else None
                })

        query = """
        INSERT INTO user_role (user_id, role_id, expired_at)
        VALUES (%(user_id)s, %(role_id)s, %(expired_at)s)
        """
        
        inserted = self.execute_many(query, data)
        return inserted