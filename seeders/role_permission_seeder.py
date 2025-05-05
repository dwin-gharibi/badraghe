from .base_seeder import BaseSeeder
from decorators.registry import get_faker, register_seeder

@register_seeder('role_permissions', dependencies=['roles', 'permissions'])
class RolePermissionSeeder(BaseSeeder):
    def seed(self, count=10):
        role_ids = self.get_random_ids('roles', min(count, 10))
        permission_ids = self.get_random_ids('permissions', min(count, 10))
        
        if not role_ids or not permission_ids:
            return 0

        data = []
        for role_id in role_ids:
            for permission_id in permission_ids[:count//len(role_ids)+1]:
                data.append({
                    "role_id": role_id,
                    "permission_id": permission_id
                })

        query = """
        INSERT INTO role_permissions (role_id, permission_id)
        VALUES (%(role_id)s, %(permission_id)s)
        """
        
        inserted = self.execute_many(query, data)
        return inserted