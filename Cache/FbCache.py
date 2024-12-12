import time
import logging
from Config.Fb import verify_firebase_token
from Config.Redis import RedisClient  

redis_client = RedisClient().connect()

# Set up logging
logging.basicConfig(
    filename='/var/log/flask_app.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def get_cached_uid_redis(id_token):
    """
    Cache the Firebase UID in Redis.
    """
    redis_connection = None
    try:
        # Start Redis connection
        redis_connection = RedisClient().connect()
        
        # Check the cache UID
        cached_uid = redis_connection.get(id_token)
        if cached_uid:
            logging.info("[get_cached_uid_redis] Cache hit for ID token.")
            return cached_uid

        logging.info("[get_cached_uid_redis] Cache miss, verifying token with Firebase.")
        
        # Verify token in Firebase
        decoded_token = verify_firebase_token(id_token)
        if not decoded_token:
            logging.warning("[get_cached_uid_redis] Token verification failed.")
            return None

        # Verify UID is returned
        firebase_uid = decoded_token.get('uid')
        if not firebase_uid:
            logging.error("[get_cached_uid_redis] Decoded token does not contain UID.")
            return None

        # Check exp time and cache UID
        expires_in = decoded_token.get('exp', time.time() + 3600) - time.time()
        if expires_in <= 0:
            logging.error("[get_cached_uid_redis] Expiration time is invalid or in past.")
            return None

        # Place token in redis
        redis_connection.setex(id_token, int(expires_in), firebase_uid)
        logging.info(f"[get_cached_uid_redis] Cached UID for {int(expires_in)} seconds.")
        return firebase_uid

    except Exception as e:
        logging.error(f"[get_cached_uid_redis] Error: {str(e)}", exc_info=True)
        return None

    finally:
        if redis_connection:
            redis_connection.close()
            logging.info("[get_cached_uid_redis] Redis connection closed.")
