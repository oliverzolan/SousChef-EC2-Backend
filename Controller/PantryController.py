import logging
from flask import Blueprint, jsonify, request
from Config.Db import Database
from Config.Fb import verify_firebase_token
from Cache.FbCache import get_cached_uid_redis
from Model.PantryModel import PantryModel
from Model.UserModel import UserModel

# Initialize the logger
logging.basicConfig(
    filename='/var/log/flask_app.log',  
    level=logging.INFO,                
    format='%(asctime)s - %(levelname)s - %(message)s'  
)

pantry_blueprint = Blueprint('pantry_blueprint', __name__)
db = Database()

@pantry_blueprint.route('/user', methods=['GET'])
def get_user_pantry():
    """
    Fetch all pantry items for the authenticated user based on Firebase token.
    """
    try:
        logging.info("Processing /user pantry request")

        # Get the Authorization token from the request headers
        id_token = request.headers.get('Authorization')
        if not id_token:
            logging.warning("Authorization token is missing in the request")
            return jsonify({"error": "Authorization token is missing"}), 401

        # Verify and cache the Firebase UID
        firebase_uid = get_cached_uid_redis(id_token)
        if not firebase_uid:
            logging.warning("Invalid or expired Firebase token")
            return jsonify({"error": "Invalid or expired Firebase token"}), 401

        # Initialize database connections and models
        connection = db.connect_read()
        user_model = UserModel(connection)
        pantry_model = PantryModel(connection)

        # Get the user ID based on Firebase UID
        user = user_model.get_user_by_firebase_uid(firebase_uid)
        if not user:
            logging.warning(f"User not found for Firebase UID: {firebase_uid}")
            return jsonify({"error": "User not found"}), 404

        user_id = user['id']
        logging.info(f"Fetched user ID: {user_id} for a verified Firebase UID")

        # Get pantry items for the user
        pantry_items = pantry_model.get_pantry_items_by_user_id(user_id)
        if not pantry_items:
            logging.info(f"No pantry items found for user ID: {user_id}")
            return jsonify({"message": "No pantry items found for this user"}), 404

        logging.info(f"Pantry items fetched for user ID: {user_id}")
        return jsonify(pantry_items), 200

    except Exception as e:
        logging.error(f"Error occurred while fetching pantry items: {str(e)}", exc_info=True)
        return jsonify({"error": "An error occurred while fetching pantry items", "details": str(e)}), 500

    finally:
        logging.info("Closing database connections for /user pantry request")
        db.close_connections()
