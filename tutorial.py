import redis
import json
import time

class CacheWithDistributedLock:
    def __init__(self, redis_client, ttl, lock_ttl=5):
        self.redis = redis_client
        self.ttl = ttl
        self.lock_ttl = lock_ttl

    def set(self, key, value):
        self.redis.setex(key, self.ttl, json.dumps(value))

    def get(self, key, fallback_function=None):
        # Try to retrieve data from cache
        value = self.redis.get(key)

        if value:
            print(f"Cache hit for key '{key}': {json.loads(value)}")
            return json.loads(value)  # Cache hit

        # Cache miss: Acquire a distributed lock to prevent the Thundering Herd Problem
        lock = self.redis.lock(f"lock:{key}", timeout=self.lock_ttl)

        if lock.acquire(blocking=False):  # Only proceed if lock is acquired
            try:
                new_value = fallback_function(key) if fallback_function else None
                if new_value:
                    self.set(key, new_value)
                    print(f"Cache miss for key '{key}', recomputing data and setting cache.")
                return new_value
            finally:
                lock.release()
        else:
            print(f"Another process is recomputing data for key '{key}', waiting for cache update...")
            while not value:
                time.sleep(0.1)  # Wait briefly before retrying
                value = self.redis.get(key)
            print(f"Retrieved updated value from cache for key '{key}': {json.loads(value)}")
            return json.loads(value) if value else None  # Return the newly cached data

redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)
cache_with_lock = CacheWithDistributedLock(
    redis_client=redis_client,
    ttl=10,
    lock_ttl=5
)

def recompute_data(key):
    time.sleep(2)  # Simulate time-consuming computation
    return {"name": f"Value for {key}"}

key = "shared_key"

# Run this in multiple terminals to observe the behavior
print(f"Retrieving value for key '{key}': {cache_with_lock.get(key, fallback_function=recompute_data)}")
