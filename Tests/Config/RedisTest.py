import redis

# Connect to Redis server
try:
    redis_client = redis.StrictRedis(host='127.0.0.1', port=6379, decode_responses=True)
    # Test connection
    if redis_client.ping():
        print("Connected to Redis!")
except Exception as e:
    print(f"Error connecting to Redis: {e}")

# Test setting and getting a key
try:
    redis_client.set("test_key", "test_value")
    value = redis_client.get("test_key")
    print(f"Value for 'test_key': {value}")
except Exception as e:
    print(f"Error performing Redis operations: {e}")
