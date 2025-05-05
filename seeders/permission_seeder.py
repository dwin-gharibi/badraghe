from .base_seeder import BaseSeeder
from decorators.registry import get_faker, register_seeder

@register_seeder('permissions')
class PermissionSeeder(BaseSeeder):
    def seed(self, count=10):
        permission_faker = get_faker('permissions')
        permissions_data = [permission_faker(self.fake) for _ in range(count)]
        
        insert_query = """
        INSERT INTO permissions (
            name, description, type, status
        ) VALUES (
            %(name)s, %(description)s, %(type)s, %(status)s
        )
        """
        
        inserted_count = self.execute_many(insert_query, permissions_data)
        return inserted_count