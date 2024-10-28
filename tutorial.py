import redis
import math
import random
import time
import json

class ProbabilisticRedisCache:
    def __init__(self, redis_client, ttl, beta=1):
        self.redis = redis_client
        self.ttl = ttl
        self.beta = beta

    def set(self, key, value, time_to_compute):
        # Pre-calculate the probabilistic TTL
        probabilistic_ttl = self.calculate_probabilistic_ttl(time_to_compute)
        print(f"TTL: '{probabilistic_ttl}'")
        self.redis.setex(key, probabilistic_ttl, json.dumps(value))  # Store data in JSON format for complex data types
    
    def get(self, key):
        value = self.redis.get(key)
        if value:
            return json.loads(value)  # Return the cached value as JSON (decoded)
        else:
            # Cache miss, re-assign the value for the missed key
            print(f"Key '{key}' not found in cache.")
            start_time = time.time()
            value = get_data(key)
            end_time = time.time()

            # Calculate the time taken for recomputation
            compute_time = end_time - start_time
            # Add 2 more seconds to describe the actual compute time
            compute_time += 2

            # Store the recomputed value with a probabilistic expiration
            self.set(key, value, compute_time)
            return value
    
    def calculate_probabilistic_ttl(self, time_to_compute):
        # Calculate probabilistic ttl based on the probabilistic expiration formula
        random_factor = abs(math.log(random.random()))  # use abs() to get the absolute number, which mean > 0
        probabilistic_ttl = self.ttl + (time_to_compute * self.beta * random_factor)
        
        return max(self.ttl, int(probabilistic_ttl))

redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)
probabilistic_redis_cache = ProbabilisticRedisCache(redis_client, ttl=10, beta=1)  # 30 seconds TTL

# Re-assign the value for the expired/missed key
def get_data(key):
    return {"name": f"Value {key}"}

keys = [f"{i}" for i in range(1, 6)]
for key in keys:
    probabilistic_redis_cache.get(key)

for key in keys:
    print(f"Retrieving value for key {key}: {probabilistic_redis_cache.get(key)}")

print("==============================================")
# Simulate waiting to reach near the expiration window for all keys
time.sleep(10)  # Wait for 10 seconds

# Access cache again for all keys (it may expire probabilistically and refresh)
for key in keys:
    print(f"Retrieving value for key {key} after sleep: {probabilistic_redis_cache.get(key)}")

print("==============================================")
# Access after expiration time for all keys (it will definitely refresh)
time.sleep(10)  # Wait for another 10 seconds
for key in keys:
    print(f"Retrieving value for key {key} after total sleep: {probabilistic_redis_cache.get(key)}")