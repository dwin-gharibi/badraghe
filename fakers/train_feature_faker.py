from decorators.registry import register_faker
from typing import List, Dict, Any

@register_faker('train_features')
def fake_train_feature(fake=None, train_ids: List[int] = None, feature_ids: List[int] = None) -> Dict[str, Any]:
    if not train_ids or not feature_ids:
        raise ValueError("train_ids and feature_ids must be provided")
    
    return {
        "train_id": fake.random_element(train_ids),
        "feature_id": fake.random_element(feature_ids)
    }