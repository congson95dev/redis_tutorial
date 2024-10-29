import asyncio
import redis.asyncio as aioredis
import json

class AsyncCacheWithPromise:
    def __init__(self, redis_client, ttl):
        self.redis = redis_client
        self.ttl = ttl
        self.promises = {}

    async def set(self, key, value):
        await self.redis.setex(key, self.ttl, json.dumps(value))

    async def get(self, key, fallback_function=None):
        value = await self.redis.get(key)

        if value:
            return json.loads(value)  # Cache hit

        # Cache miss: Check if a Future already exists for this key
        if key in self.promises:
            print(f"Cache miss for key '{key}', waiting on existing promise.")
            result = await self.promises[key]
            return result

        # Create a new Future for the key
        print(f"Cache miss for key '{key}', creating new promise.")
        self.promises[key] = asyncio.Future()

        try:
            new_value = await fallback_function(key) if fallback_function else None
            if new_value:
                self.promises[key].set_result(new_value)
                await self.set(key, new_value)
            return new_value
        finally:
            del self.promises[key]

async def recompute_data(key):
    await asyncio.sleep(5)  # Simulate long computation
    return {"name": f"Value for {key}"}

async def run_request(cache, key, delay, request_num):
    await asyncio.sleep(delay)  # Delay the start of this task
    result = await cache.get(key, fallback_function=recompute_data)
    print(f"Fetch result from request {request_num}: {result}")

async def main():
    redis_client = await aioredis.from_url("redis://localhost")
    cache_with_promise = AsyncCacheWithPromise(redis_client=redis_client, ttl=10)

    key = "shared_key"

    tasks = [
        run_request(cache_with_promise, key, delay=i * 1, request_num=i+1)
        for i in range(4)
    ]

    await asyncio.gather(*tasks)

    await redis_client.aclose()

asyncio.run(main())
