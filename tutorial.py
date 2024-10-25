# pip install redis
import redis, json

redis_client = redis.Redis(host='localhost', port=6379, db=0)

def get_data():
    return {"name": "Fudo"}

data = redis_client.get('data')
if data is None:
    print("not found in redis, run function get_data()")
    data = get_data()
    # store data as cache to redis
    redis_client.set('data', json.dumps(data))
else:
    print("founded in redis")
    # load data from redis
    data = json.loads(data)

print(data)

