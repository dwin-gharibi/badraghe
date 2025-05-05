from functools import wraps
from typing import Dict, Any, Callable, Optional, List

FAKER_REGISTRY: Dict[str, Callable] = {}
SEEDER_REGISTRY: Dict[str, Dict[str, Any]] = {}

def register_faker(table_name: str) -> Callable:
    def decorator(faker_func: Callable) -> Callable:
        FAKER_REGISTRY[table_name] = faker_func
        @wraps(faker_func)
        def wrapper(*args, **kwargs):
            return faker_func(*args, **kwargs)
        return wrapper
    return decorator

def register_seeder(table_name: str, dependencies: Optional[List[str]] = None) -> Callable:
    def decorator(seeder_class: type) -> type:
        SEEDER_REGISTRY[table_name] = {
            'class': seeder_class,
            'dependencies': dependencies or []
        }
        @wraps(seeder_class)
        def wrapper(*args, **kwargs):
            return seeder_class(*args, **kwargs)
        return wrapper
    return decorator

def get_faker(table_name: Optional[str] = None) -> Any:
    if table_name:
        return FAKER_REGISTRY.get(table_name)
    return FAKER_REGISTRY

def get_seeder(table_name: Optional[str] = None) -> Any:
    if table_name:
        return SEEDER_REGISTRY.get(table_name)
    return SEEDER_REGISTRY