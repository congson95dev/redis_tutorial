# pip install redis
import redis, json

redis_client = redis.Redis(host='localhost', port=6379, db=0)

def get_data():
    return {"name": "Fudo"}

# caching to redis with json format
# check if data is cached in redis yet, if not, call to function get_data() and store the result as cache in redis
# else, get the data from redis
# this will so much faster than just calling to the function

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

