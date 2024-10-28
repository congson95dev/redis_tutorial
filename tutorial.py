import redis
import json
import time
import threading

class EarlyRecomputeCache:
    def __init__(self, redis_client, ttl, recompute_threshold):
        self.redis = redis_client
        self.ttl = ttl
        self.recompute_threshold = recompute_threshold

    def set(self, key, value):
        self.redis.setex(key, self.ttl, json.dumps(value))

    def get(self, key, fallback_function):
        value = self.redis.get(key)
        print(f"TTL: '{self.redis.ttl(key)}'")

        if value:
            data = json.loads(value)
            ttl_remaining = self.redis.ttl(key)
            
            # Trigger early recomputation if near expiration
            if ttl_remaining <= self.recompute_threshold:
                print(f"Key '{key}' is near expiration (TTL: {ttl_remaining}s). Recomputing in the background.")
                threading.Thread(target=self._recompute_in_background, args=(key, fallback_function)).start()

            return data

        # Cache miss: compute and set the cache
        print(f"Cache miss for key '{key}', computing and setting cache.")
        new_value = fallback_function(key)
        self.set(key, new_value)
        return new_value

    def _recompute_in_background(self, key, fallback_function):
        new_value = fallback_function(key)
        self.set(key, new_value)
        print(f"Background recompute complete for key '{key}'.")

def recompute_data(key):
    time.sleep(2)  # Simulate a long computation time
    return {"name": f"Value for key {key}"}

redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)
cache = EarlyRecomputeCache(redis_client=redis_client, ttl=10, recompute_threshold=3)  # 10s TTL, recompute when <3s remaining

key = "1"
cache.set(key, recompute_data(key))

# Access cache and trigger early recomputation
print("First retrieval:", cache.get(key, fallback_function=recompute_data))
print("\nWaiting 7 seconds to reach recompute threshold...")
time.sleep(7)

# Retrieve again, should trigger early recomputation
print("Second retrieval:", cache.get(key, fallback_function=recompute_data))

# Give the background thread some time to complete
time.sleep(3)
print("\nRetrieving after background recompute complete:", cache.get(key, fallback_function=recompute_data))

# Final check to see if the key isn't expired
time.sleep(2)
print("\nFinal retrieval:", cache.get(key, fallback_function=recompute_data))
