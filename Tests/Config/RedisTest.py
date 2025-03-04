import redis
import unittest

class TestRedisConnection(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        try:
            cls.redis_client = redis.StrictRedis(host='127.0.0.1', port=6379, decode_responses=True)
            cls.redis_client.ping()  # Test connection
            print("Connected to Redis")
        except Exception as e:
            print(f"Error connecting to Redis: {e}")
            cls.redis_client = None  # Mark as None if connection fails

    def test_redis_connection(self):
        if self.redis_client:
            self.assertTrue(self.redis_client.ping(), "Redis should respond")
        else:
            self.fail("Redis connection failed.")

    def test_set_get_key(self):
        if self.redis_client:
            self.redis_client.set("test_key", "test_value")
            value = self.redis_client.get("test_key")
            self.assertEqual(value, "test_value", "Redis should return the correct value")
        else:
            self.fail("Redis connection failed")

    @classmethod
    def tearDownClass(cls):
        """Clean up after tests"""
        if cls.redis_client:
            cls.redis_client.delete("test_key") 
            print("Test data removed from Redis.")

if __name__ == "__main__":
    unittest.main()
