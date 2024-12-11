import os
import redis
from dotenv import load_dotenv

load_dotenv()  

class RedisClient:
    def __init__(self):
        self.host = os.getenv("REDIS_HOST") 
        self.port = int(os.getenv("REDIS_PORT")   
        self.db = int(os.getenv("REDIS_DB")          
        self.redis_client = None

    def connect(self):
        """
        Establish and return a Redis connection.
        """
        if not self.redis_client:
            self.redis_client = redis.StrictRedis(
                host=self.host,
                port=self.port,
                db=self.db,
                decode_responses=True
            )
            print(f"Connected to Redis at {self.host}:{self.port} (DB: {self.db})")
        return self.redis_client

    def close(self):
        """
        Close the Redis connection if it exists.
        """
        if self.redis_client:
            self.redis_client.close()
            print("Redis connection closed.")
            self.redis_client = None
