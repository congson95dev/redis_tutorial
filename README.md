# redis_tutorial

## Start virtual environment

`sudo pip3 install virtualenv`

`python3 -m venv venv`

`source venv/bin/activate`

## Run

`pip install redis redisbloom`

`docker run --name redis-bloom -p 6380:6379 -d redislabs/rebloom:latest`

`python3 tutorial.py`

## Bloom Filter

### Explaination:

<b>Initial Cache Check</b>: The `get_data` function first checks if the key is already cached in Redis. If it is, it returns the data directly.

<b>Bloom Filter Validation</b>: If the cache miss occurs, we check if the key is in the Bloom filter:
- If not in the Bloom filter, we assume it is an invalid or first-time key and look it up in the database.
- If the key does not exist in the database, it is added to a <b>negative cache</b> in Redis to prevent repeated invalid requests from hitting the database.
- If the key exists in the database, it is added to both the Bloom filter and the Redis cache.

<b>Handle False Positives</b>: If the Bloom filter indicates a possible match but the key does not exist in the database, it could be a <b>false positive</b>. In this case, the key is also added to the negative cache.

### Result:

![alt text](image.png)

As you see, in the Step 1, `user_1` and `user_2` on the first call is accessed to the DB.

But in Step 2, since they already cached, they return the value immediately without access to the DB.

Also, for the `user_4`, since this key isn't exists in DB, so in the Step 1, it's added to `negative_cache` and marked as invalid key, and in Step 2, since it's exists in `negative_cache`, so it return error immediately.

Reference links:

1. list command

https://redis.io/docs/latest/commands/?group=bf

2. strateries on using Bloom Filter

https://stackoverflow.com/a/74515080/8962929



