from .base_seeder import BaseSeeder
from decorators.registry import get_faker, register_seeder

@register_seeder('features')
class FeatureSeeder(BaseSeeder):
    def seed(self, count=10):
        feature_faker = get_faker('features')
        features_data = [feature_faker(self.fake) for _ in range(count)]
        
        insert_query = """
        INSERT INTO features (
            name, description
        ) VALUES (
            %(name)s, %(description)s
        )
        """
        
        inserted_count = self.execute_many(insert_query, features_data)
        return inserted_count