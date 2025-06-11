import json
import os
from app.redis import redis_client, get_redis

async def set_cache(key: str, value, expire_seconds: int = 60):
    redis = await get_redis()
    value_str = json.dumps(value)
    await redis.set(key, value_str, ex=expire_seconds)

async def get_cache(key: str):
    redis = await get_redis()
    value = await redis.get(key)
    return json.loads(value) if value else None

async def delete_cache(key: str):
    redis = await get_redis()
    await redis.delete(key)
