from .base_seeder import BaseSeeder
from decorators.registry import get_faker, register_seeder

@register_seeder('flight_features', dependencies=['flight_details', 'features'])
class FlightFeatureSeeder(BaseSeeder):
    def seed(self, count=10):
        flight_feature_faker = get_faker('flight_features')
        if not flight_feature_faker:
            raise ValueError("No faker registered for 'flight_features' table")

        flight_ids = self.get_random_ids('flight_details', min(count, 10))
        feature_ids = self.get_random_ids('features', min(count, 5))
        
        if not flight_ids or not feature_ids:
            return 0

        pairs = set()
        while len(pairs) < count and len(pairs) < len(flight_ids) * len(feature_ids):
            pair = (
                self.fake.random_element(flight_ids),
                self.fake.random_element(feature_ids)
            )
            pairs.add(pair)

        data = [{"flight_id": fid, "feature_id": feature_id} for fid, feature_id in pairs]

        insert_query = """
        INSERT IGNORE INTO flight_features (
            flight_id, feature_id
        ) VALUES (
            %(flight_id)s, %(feature_id)s
        )
        """
        
        inserted_count = self.execute_many(insert_query, data)
        return inserted_count