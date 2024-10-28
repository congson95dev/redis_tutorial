import redis
import random
import time
import json

class ProbabilisticRedisCache:
    def __init__(self, redis_client, ttl, early_expiration_factor=0.1):
        self.redis = redis_client
        self.ttl = ttl
        self.early_expiration_factor = early_expiration_factor

    def set(self, key, value):
        self.redis.setex(key, self.ttl, json.dumps(value))  # Store data in JSON format for complex data types
    
    def get(self, key, fallback_function=None):
        current_time = time.time()
        
        value = self.redis.get(key)
        if value:
            # Get the remaining time to live for the key
            ttl_remaining = self.redis.ttl(key)
            expiration_time = current_time + ttl_remaining
            
            # Check if the value should expire probabilistically
            if self.is_probabilistically_expired(expiration_time, current_time):
                print(f"Key '{key}' has expired probabilistically.")
                if (fallback_function):
                    # Re-assign the value
                    new_value = fallback_function(key)
                    self.set(key, new_value)
                    return new_value
                return value
            return json.loads(value)  # Return the cached value as JSON (decoded)
        else:
            # Cache miss, re-assign the value for the missed key
            print(f"Key '{key}' not found in cache.")
            if (fallback_function):
                new_value = fallback_function(key)
                self.set(key, new_value)
                return new_value
            return value
    
    def is_probabilistically_expired(self, expiration_time, current_time):
        # Calculate the early expiration window
        early_expiration_window = self.ttl * self.early_expiration_factor
        if expiration_time - current_time <= early_expiration_window:
            expiration_probability = (early_expiration_window - (expiration_time - current_time)) / early_expiration_window
            return random.random() < expiration_probability
        return False


redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)
cache = ProbabilisticRedisCache(redis_client, ttl=30, early_expiration_factor=0.5)  # 30 seconds TTL, 50% early expiration window

# Re-assign the value for the expired/missed key
def get_data(key):
    return {"name": f"Data for {key}"}

keys = [f"my_key_{i}" for i in range(1, 11)]
for key in keys:
    cache.set(key, get_data(key))

for key in keys:
    print(f"Retrieving value for {key}: {cache.get(key, fallback_function=get_data)}")

print("==============================================")
# Simulate waiting to reach near the expiration window for all keys
time.sleep(25)  # Wait for 25 seconds

# Access cache again for all keys (it may expire probabilistically and refresh)
for key in keys:
    print(f"Retrieving value for {key} after sleep: {cache.get(key, fallback_function=get_data)}")

print("==============================================")
# Access after expiration time for all keys (it will definitely refresh)
time.sleep(10)  # Wait for another 10 seconds
for key in keys:
    print(f"Retrieving value for {key} after total sleep: {cache.get(key)}")
