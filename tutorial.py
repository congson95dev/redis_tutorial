import json
from tasks import listen_for_expiration_events, get_data, redis_client

def initialize_data():
    data = get_data()
    redis_client.setex('data', 10, json.dumps(data))
    return data

data = initialize_data()
print("Initial data:", data)

# Start the event listener (this can run in the background)
listen_for_expiration_events.delay()