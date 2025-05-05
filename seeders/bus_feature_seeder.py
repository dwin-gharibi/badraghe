from .base_seeder import BaseSeeder
from decorators.registry import get_faker, register_seeder

@register_seeder('bus_features', dependencies=['bus_details', 'features'])
class BusFeatureSeeder(BaseSeeder):
    def seed(self, count=10):
        bus_feature_faker = get_faker('bus_features')
        if not bus_feature_faker:
            raise ValueError("No faker registered for 'bus_features' table")

        bus_ids = self.get_random_ids('bus_details', min(count, 10))
        feature_ids = self.get_random_ids('features', min(count, 5))
        
        if not bus_ids or not feature_ids:
            return 0

        pairs = set()
        while len(pairs) < count and len(pairs) < len(bus_ids) * len(feature_ids):
            pair = (
                self.fake.random_element(bus_ids),
                self.fake.random_element(feature_ids)
            )
            pairs.add(pair)

        data = [{"bus_id": bid, "feature_id": fid} for bid, fid in pairs]

        insert_query = """
        INSERT IGNORE INTO bus_features (
            bus_id, feature_id
        ) VALUES (
            %(bus_id)s, %(feature_id)s
        )
        """
        
        inserted_count = self.execute_many(insert_query, data)
        return inserted_count