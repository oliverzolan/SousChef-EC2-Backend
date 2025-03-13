import time
import logging
from Config.Redis import RedisClient  
from Auth.FatSecretAuth import FatSecretAuth

redis_client = RedisClient().connect()

# Set up logging
logging.basicConfig(
    filename='/var/log/flask_app.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def get_cached_fatsecret_token():
    """
    Fetch and cache FatSecret access token in Redis.
    """
    redis_connection = None
    try:
        redis_connection = RedisClient().connect()
        
        cached_token = redis_connection.get("fatsecret_token")
        if cached_token:
            logging.info("[get_cached_fatsecret_token] Cache hit for FatSecret token.")
            return cached_token.decode("utf-8")

        logging.info("[get_cached_fatsecret_token] Cache miss, requesting new token.")
        
        fatsecret_auth = FatSecretAuth(region_name="us-east-1")  
        new_token = fatsecret_auth.fetch_access_token()
        
        if not new_token:
            logging.error("[get_cached_fatsecret_token] Failed to fetch new FatSecret token.")
            return None

        expires_in = 3600 

        redis_connection.setex("fatsecret_token", expires_in, new_token)
        logging.info(f"[get_cached_fatsecret_token] Cached FatSecret token for {expires_in} seconds.")

        return new_token

    except Exception as e:
        logging.error(f"[get_cached_fatsecret_token] Error: {str(e)}", exc_info=True)
        return None

    finally:
        if redis_connection:
            redis_connection.close()
            logging.info("[get_cached_fatsecret_token] Redis connection closed.")
