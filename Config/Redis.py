import os
import redis
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

REDIS_HOST = os.getenv("REDIS_HOST")
REDIS_PORT = os.getenv("REDIS_PORT")
REDIS_DB = os.getenv("REDIS_DB")

class RedisClient:
    def __init__(self):
        self.host = REDIS_HOST
        self.port = REDIS_PORT
        self.db = REDIS_DB
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
        return self.redis_client
