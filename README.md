# redis_tutorial

Start virtual environment

`sudo pip3 install virtualenv`

`python3 -m venv venv`

`source venv/bin/activate`

Run

`pip install redis`

`docker run --name redis-server -p 6379:6379 -d redis`

`python3 tutorial.py`

## Exeternal computation - early recomputation

Use `redis event` as a `pubsub` to check if the key is expired, if it does, then automatic re-assign.

Result:

![alt text](image.png)

As you can see, the app has found the key expired 2 times, and it automatic re-assined.

### Alternative approach

We could also use `python schedule` to check every 1 seconds to see if any key is expired, if it does, then automatic re-assign.