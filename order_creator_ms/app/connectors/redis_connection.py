import redis
import os

REDIS_HOST = os.environ.get('REDIS_HOST', '172.19.0.112')
REDIS_PORT = int(os.environ.get('REDIS_PORT', 6379))
REDIS_DB = int(os.environ.get('REDIS_DB', 0))

class RedisConnection:
    def __init__(self, redis_client=None):
        self.redis_client = redis_client or redis.Redis(
            host=REDIS_HOST,
            port=REDIS_PORT,
            db=REDIS_DB,
            decode_responses=True
        )

    def get_client(self):
        """Return the Redis client."""
        return self.redis_client
