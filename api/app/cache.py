import redis
import json

# Connects to Redis container
redis_client = redis.Redis(host='redis_cache', port=6379, password='redis_pass', decode_responses=True)

def get_cached_file(file_hash: str):
    cached = redis_client.get(file_hash)
    return json.loads(cached) if cached else None

def set_cached_file(file_hash: str, data: dict, expire: int = 3600):
    redis_client.setex(file_hash, expire, json.dumps(data))