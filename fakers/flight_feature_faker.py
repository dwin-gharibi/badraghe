from decorators.registry import register_faker
from typing import List, Dict, Any

@register_faker('flight_features')
def fake_flight_feature(fake=None, flight_ids: List[int] = None, feature_ids: List[int] = None) -> Dict[str, Any]:
    if not flight_ids or not feature_ids:
        raise ValueError("flight_ids and feature_ids must be provided")
    
    return {
        "flight_id": fake.random_element(flight_ids),
        "feature_id": fake.random_element(feature_ids)
    }