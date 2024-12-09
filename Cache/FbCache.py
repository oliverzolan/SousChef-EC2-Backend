import time
import logging
from Config.Fb import verify_firebase_token
from Config.Redis import RedisClient  

# Initialize Redis client
redis_client = RedisClient().connect()

# Set up logging
logging.basicConfig(
    filename='/var/log/flask_app.log',  # Adjust the path if needed
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def get_cached_uid_redis(id_token):
    """
    Cache the Firebase UID verification using Redis.
    """
    try:
        # Check the cache for the UID
        cached_uid = redis_client.get(id_token)
        if cached_uid:
            logging.info("[get_cached_uid_redis] Cache hit for ID token.")
            return cached_uid

        logging.info("[get_cached_uid_redis] Cache miss, verifying token with Firebase.")
        
        # Verify token using Firebase
        decoded_token = verify_firebase_token(id_token)
        if not decoded_token:
            logging.warning("[get_cached_uid_redis] Token verification failed.")
            return None

        firebase_uid = decoded_token.get('uid')
        if not firebase_uid:
            logging.error("[get_cached_uid_redis] Decoded token does not contain 'uid'.")
            return None

        # Calculate expiration time and cache the UID
        expires_in = decoded_token.get('exp', time.time() + 3600) - time.time()
        if expires_in <= 0:
            logging.error("[get_cached_uid_redis] Expiration time is invalid or in the past.")
            return None

        redis_client.setex(id_token, int(expires_in), firebase_uid)
        logging.info(f"[get_cached_uid_redis] Cached UID for {int(expires_in)} seconds.")
        return firebase_uid

    except Exception as e:
        logging.error(f"[get_cached_uid_redis] Error: {str(e)}", exc_info=True)
        return None
