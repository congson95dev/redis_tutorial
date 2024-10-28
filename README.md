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

## Redlock

Lock the call until the cache is updated. <br>
For example: there are 1000 requests that call to the same key, in this case, Redlock will lock all of them, only let the 1st request to process and re-assign the key, after finish, we will release the lock and let other requests to access.

Result:

![alt text](image.png)

As you see, when 2 request calling at the same time, the Redlock lock the 2nd request until the cache is updated.