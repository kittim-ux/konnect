import json
import redis
import time

# Initialize the Redis client
redis_client = redis.StrictRedis(host='127.0.0.1', port=6379, db=0)

def is_data_sent(name):
    return redis_client.exists(name)

def cache_data(name):
    # Convert the expiration time to an integer
    expiration_time = int(30 * 60)  # 2 minutes in seconds

    # Store the building name in the Redis cache with the updated expiration time
    redis_client.setex(name, expiration_time, json.dumps({'timestamp': time.time()}))
