import redis
import json

redis_client = redis.Redis(host='localhost', port=6379, db=0)
redis_client.config_set("notify-keyspace-events", "Ex")

pubsub = redis_client.pubsub()
pubsub.psubscribe("__keyevent@0__:expired")

def get_data():
    return {"name": "Fudo"}

def initialize_data():
    data = get_data()
    redis_client.setex('data', 10, json.dumps(data))
    return data

def recompute_and_update_data():
    new_data = get_data()
    redis_client.setex('data', 10, json.dumps(new_data))
    print("Recomputed and refreshed expired key: 'data'")

data = initialize_data()
print("Initial data:", data)

print("Listening for expired keys...")
for message in pubsub.listen():
    if message['type'] == 'pmessage' and message['data'].decode() == 'data':
        recompute_and_update_data()