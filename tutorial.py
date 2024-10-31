import redis
import json
import time
from redisbloom.client import Client as BloomFilterClient

redis_client = redis.StrictRedis(host='localhost', port=6380, db=0)
bloom_filter = BloomFilterClient(host='localhost', port=6380, db=0)

BLOOM_FILTER_KEY = "valid_keys_bf"
NEGATIVE_CACHE_TTL = 60
DATA_CACHE_TTL = 300

# Initialize the Bloom filter
if not redis_client.exists(BLOOM_FILTER_KEY):
    bloom_filter.bfCreate(BLOOM_FILTER_KEY, errorRate=0.001, capacity=10000)

# Fallback function to simulate data fetching from the database
def fetch_data_from_db(key):
    time.sleep(2)
    if key in ["user_1", "user_2", "user_3"]:
        return {"user_id": key, "name": f"User {key[-1]}"}
    return None

def get_data(key):
    data = redis_client.get(key)
    if data:
        return json.loads(data)  # Cache hit

    # Cache miss: Check if the key is exist in Bloom filter

    # Key not in Bloom filter, it could because 2 cases:
    # 1. key invalid
    # 2. first-time request
    if not bloom_filter.bfExists(BLOOM_FILTER_KEY, key):
        # Check Redis for negative cache entry to prevent repeated DB hits
        if redis_client.get(f"negative_cache:{key}"):
            # case 1: key invalid
            print(f"Cache miss for invalid key '{key}', bypassing DB.")
            return None

        # case 2: first-time request
        result = fetch_data_from_db(key) # Fetch DB
        if result:
            # Key is valid, add it to Bloom filter and cache
            bloom_filter.bfAdd(BLOOM_FILTER_KEY, key)
            redis_client.setex(key, DATA_CACHE_TTL, json.dumps(result))
            return result
        else:
            # Key is invalid, add it to negative cache to prevent repeated DB hits
            redis_client.setex(f"negative_cache:{key}", NEGATIVE_CACHE_TTL, "invalid")
            print(f"Invalid key '{key}', added to negative cache.")
            return None

    # Key exists in the Bloom filter, it could be the 2 cases:
    # 1. key valid
    # 2. false positive
    print(f"Bloom filter hit for key '{key}', fetching data from DB.")
    result = fetch_data_from_db(key)
    if result: # case 1: key valid
        redis_client.setex(key, DATA_CACHE_TTL, json.dumps(result))
        return result
    else:
        # case 2: false positive
        # adding the key to the negate_cache so next time we won't have to fetch DB with the invalid key
        redis_client.setex(f"negative_cache:{key}", NEGATIVE_CACHE_TTL, "invalid")
        return None

keys_to_test = ["user_1", "user_2", "user_4"]

for i in range(2):
    print(f"Step '{i+1}':")
    for key in keys_to_test:
        print(f"Fetching data for {key}: {get_data(key)}")
    print("===================")