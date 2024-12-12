import os
import redis
from dotenv import load_dotenv

load_dotenv()  

class RedisClient:
    """
    Redis configuration connection and close.
    """
    def __init__(self):
        self.host = os.getenv("REDIS_HOST") 
        self.port = int(os.getenv("REDIS_PORT")) 
        self.db = os.getenv("REDIS_DB")     
        self.redis_client = None

    def connect(self):
        # Establish connection
        if not self.redis_client:
            self.redis_client = redis.StrictRedis(
                host=self.host,
                port=self.port,
                db=self.db,
                decode_responses=True
            )
        return self.redis_client

    def close(self):
        # Close connection
        if self.redis_client:
            self.redis_client.close()
            print("Redis connection closed.")
            self.redis_client = None
