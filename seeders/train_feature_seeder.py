from .base_seeder import BaseSeeder
from decorators.registry import get_faker, register_seeder

@register_seeder('train_features', dependencies=['train_details', 'features'])
class TrainFeatureSeeder(BaseSeeder):
    def seed(self, count=10):
        train_feature_faker = get_faker('train_features')
        if not train_feature_faker:
            raise ValueError("No faker registered for 'train_features' table")

        train_ids = self.get_random_ids('train_details', min(count, 10))
        feature_ids = self.get_random_ids('features', min(count, 5))
        
        if not train_ids or not feature_ids:
            return 0

        pairs = set()
        while len(pairs) < count and len(pairs) < len(train_ids) * len(feature_ids):
            pair = (
                self.fake.random_element(train_ids),
                self.fake.random_element(feature_ids)
            )
            pairs.add(pair)

        data = [{"train_id": tid, "feature_id": fid} for tid, fid in pairs]

        insert_query = """
        INSERT IGNORE INTO train_features (
            train_id, feature_id
        ) VALUES (
            %(train_id)s, %(feature_id)s
        )
        """
        
        inserted_count = self.execute_many(insert_query, data)
        return inserted_count