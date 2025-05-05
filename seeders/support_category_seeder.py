from .base_seeder import BaseSeeder
from decorators.registry import get_faker, register_seeder

@register_seeder('support_categories')
class SupportCategorySeeder(BaseSeeder):
    def seed(self, count=10):
        category_faker = get_faker('support_categories')
        categories_data = [category_faker(self.fake) for _ in range(count)]
        
        insert_query = """
        INSERT INTO support_categories (
            name, description
        ) VALUES (
            %(name)s, %(description)s
        )
        """
        
        inserted_count = self.execute_many(insert_query, categories_data)
        return inserted_count