# redis_tutorial

## Start virtual environment

`sudo pip3 install virtualenv`

`python3 -m venv venv`

`source venv/bin/activate`

## Run

`pip install redis`

`docker run --name redis-server -p 6379:6379 -d redis`

`python3 tutorial.py`

## Probalilistic early expiration

Pre-calculate the probalilistic to see if the cache key is about to expired, then randomly pre-expired it and re-assign the data for that key

The formula to probalilistic is noted detail in `is_probabilistically_expired()` function

Result:

![alt text](image.png)

As you see, some of the keys are pre-expired and re-assigned before the actual expired time occur.