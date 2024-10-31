# redis_tutorial

## Start virtual environment

`sudo pip3 install virtualenv`

`python3 -m venv venv`

`source venv/bin/activate`

## Run

`pip install redis`

`docker run --name redis-server -p 6379:6379 -d redis`

Open 2 terminal and run:

`python3 tutorial.py`

## Promise (asyncio.Future)

Pending the call until the cache is updated. <br>
For example: there are 1000 requests that call to the same key, in this case, `asyncio.Future` will pending all of them, only let the 1st request to process and re-assign the key, after finish, `asyncio.Future` will return the value to all requests, and after that, we delete the lock.

Result:

![alt text](image.png)

As you see, when 4 request calling at the same time, the `asyncio.Future` pending all the requests from 2nd until the cache is updated.