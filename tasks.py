import json
import redis
from celery import Celery

app = Celery('tasks', broker='redis://localhost:6379/0')

redis_client = redis.Redis(host='localhost', port=6379, db=0)
redis_client.config_set("notify-keyspace-events", "Ex")

pubsub = redis_client.pubsub()
pubsub.psubscribe("__keyevent@0__:expired")

def get_data():
    return {"name": "Fudo"}

@app.task
def recompute_and_update_data():
    new_data = get_data()
    redis_client.setex('data', 10, json.dumps(new_data))
    print("Recomputed and refreshed expired key: 'data'")

@app.task
def listen_for_expiration_events():
    print("Celery worker listening for expired keys...")

    for message in pubsub.listen():
        if message['type'] == 'pmessage' and message['data'].decode() == 'data':
            recompute_and_update_data.delay()