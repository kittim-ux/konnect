import os
import json
from redis import Redis
import redis
from dotenv import load_dotenv
from datetime import timedelta

# Initialize the Redis client
load_dotenv()
REDIS_HOST = os.getenv('redis_host')
REDIS_PORT = os.getenv('redis_port')
REDIS_DB = os.getenv('redis_db')
redis_client = Redis(host=REDIS_HOST, port=int(REDIS_PORT), db=int(REDIS_DB))

def cache_data(bucket, serial_number, data, duration=None):
    # Create a cache key based on bucket and serial_number
    cache_key = f"{bucket}_{serial_number}"
    # Serialize and cache the data in Redis
    if duration:
        # If a duration is specified, use it to set an expiration time for the cache
        redis_client.setex(cache_key, duration, json.dumps(data))
    else:
        # If no duration is specified, cache the data indefinitely (existing behavior)
        redis_client.set(cache_key, json.dumps(data))

def not_confirmed(bucket, serial_number, data_entry):
    # Call the cache_data function with a 5-minute duration (10800 seconds)
    cache_data(bucket, serial_number, data_entry, duration=10800)

def get_cached_data(bucket, serial_number):
    # Create a cache key based on bucket and serial_number
    cache_key = f"{bucket}_{serial_number}"
    # Retrieve and deserialize the cached data from Redis
    cached_data = redis_client.get(cache_key)
    if cached_data:
        return json.loads(cached_data)
    else:
        return None

def get_all_cached_data():
    # Retrieve all cache keys
    cache_keys = redis_client.keys("*")
    cached_data = {}

    for cache_key in cache_keys:
        # Retrieve the cached data
        cached_value = redis_client.get(cache_key)
        if cached_value:
            # Deserialize the cached data and store it in a dictionary
            try:
                data = json.loads(cached_value)
                cached_data[cache_key.decode()] = data
            except json.JSONDecodeError as e:
                print(f"Error decoding cached data for key {cache_key.decode()}: {e}")

    return cached_data

def view_cached_data():
    # Call the function to get all cached data
    all_cached_data = get_all_cached_data()

    # Print all cached data
    for cache_key, data in all_cached_data.items():
        print(f"Cache Key: {cache_key}")
        print("Cached Data:")
        print(data)

 #Initialize the Redis client
if __name__ == "__main__":
    view_cached_data()




