import os
import json
from redis import Redis
from dotenv import load_dotenv

# Initialize the Redis client
load_dotenv()
REDIS_HOST = os.getenv('redis_host')
REDIS_PORT = os.getenv('redis_port')
REDIS_DB = os.getenv('redis_db')
redis_client = Redis(host=REDIS_HOST, port=int(REDIS_PORT), db=int(REDIS_DB))

def cache_data(bucket, serial_number, data):
    # Create a cache key based on bucket and serial_number
    cache_key = f"{bucket}_{serial_number}"
    # Serialize and cache the data in Redis
    redis_client.setex(cache_key, 60 * 60 * 24 * 365, json.dumps(data))

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

# Example usage:
if __name__ == "__main__":
    view_cached_data()  # Uncomment this line to view cached data from the same script




