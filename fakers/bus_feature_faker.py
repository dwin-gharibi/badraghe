from decorators.registry import register_faker
from typing import List, Dict, Any

@register_faker('bus_features')
def fake_bus_feature(fake=None, bus_ids: List[int] = None, feature_ids: List[int] = None) -> Dict[str, Any]:
    if not bus_ids or not feature_ids:
        raise ValueError("bus_ids and feature_ids must be provided")
    
    return {
        "bus_id": fake.random_element(bus_ids),
        "feature_id": fake.random_element(feature_ids)
    }