from .base_seeder import BaseSeeder
from decorators.registry import get_faker, register_seeder

@register_seeder('roles')
class RoleSeeder(BaseSeeder):
    def seed(self, count=10):
        role_faker = get_faker('roles')
        roles_data = [role_faker(self.fake) for _ in range(count)]
        
        insert_query = """
        INSERT INTO roles (
            name, description, parent_role_id, status
        ) VALUES (
            %(name)s, %(description)s, %(parent_role_id)s, %(status)s
        )
        """
        
        inserted_count = self.execute_many(insert_query, roles_data)
        return inserted_count