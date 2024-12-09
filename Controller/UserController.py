import logging
from flask import Blueprint, jsonify, request
from Config.Db import Database
from Config.Fb import verify_firebase_token
from Cache.FbCache import get_cached_uid_redis
from Model.UserModel import UserModel

# Initialize the logger
logging.basicConfig(
    filename='/var/log/flask_app.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

user_blueprint = Blueprint('user', __name__)
db = Database()

@user_blueprint.route('/create', methods=['POST'])
def create_user():
    """
    Create a new user in the database when an account is created.
    """
    try:
        logging.info("[/create] Processing user creation request")

        # Get the Authorization token and email from the request
        id_token = request.headers.get('Authorization')
        email = request.headers.get('Email')

        if not id_token or not email:
            if not id_token:
                logging.warning("[/create] Authorization token is missing in the request")
            if not email:
                logging.warning("[/create] Email is missing in the request")
            return jsonify({"error": "Authorization token or email is missing"}), 400

        # Verify and cache the Firebase UID
        firebase_uid = get_cached_uid_redis(id_token)
        if not firebase_uid:
            logging.warning("[/create] Invalid or expired Firebase token")
            return jsonify({"error": "Invalid or expired Firebase token"}), 401

        # Establish a write connection
        logging.info("[/create] Establishing write connection to the database")
        connection = db.connect_write()
        user_model = UserModel(connection)

        # Check if the user already exists
        existing_user = user_model.get_user_by_firebase_uid(firebase_uid)
        if existing_user:
            logging.info(f"[/create] User already exists: {existing_user['id']}")
            return jsonify({"message": "User already exists", "user_id": existing_user['id']}), 200

        # Insert the new user into the database
        user_id = user_model.create_user(firebase_uid, email)
        logging.info(f"[/create] New user created with ID: {user_id}")

        return jsonify({"message": "User created successfully", "user_id": user_id}), 201

    except Exception as e:
        logging.error(f"[/create] Error occurred while creating user: {str(e)}", exc_info=True)
        return jsonify({"error": "An error occurred while creating the user", "details": str(e)}), 500

    finally:
        logging.info("[/create] Closing database connections")
        db.close_connections()

