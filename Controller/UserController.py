import logging
from flask import Blueprint, jsonify, request
from Config.Db import Database
from Config.Fb import verify_firebase_token
from Cache.FbCache import get_cached_uid_redis
from Model.UserModel import UserModel

class UserController:
    """
    Controller with routes, function calling, error handling, and logging.
    """
    def __init__(self):
        self.blueprint = Blueprint('user', __name__)
        self.db = Database()

        # Initialize the logger
        logging.basicConfig(
            filename='/var/log/flask_app.log',
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)

        # Routes
        self.blueprint.add_url_rule('/create', view_func=self.create_user, methods=['POST'])

    def create_user(self):
        """
        Create user in Database.
        """
        try:
            self.logger.info("[/create] Processing user creation request")

            id_token = request.headers.get('Authorization')
            email = request.headers.get('Email')

            if not id_token or not email:
                if not id_token:
                    self.logger.warning("[/create] Authorization token is missing in the request")
                if not email:
                    self.logger.warning("[/create] Email is missing in the request")
                return jsonify({"error": "Authorization token or email is missing"}), 400

            # Get UID
            firebase_uid = get_cached_uid_redis(id_token)
            if not firebase_uid:
                self.logger.warning("[/create] Invalid or expired Firebase token")
                return jsonify({"error": "Invalid or expired Firebase token"}), 401

            # Establish database connection
            self.logger.info("[/create] Establishing write connection to the database")
            connection = self.db.connect_write()
            user_model = UserModel(connection)

            # Check if user exist
            existing_user = user_model.get_user_by_firebase_uid(firebase_uid)
            if existing_user:
                self.logger.info(f"[/create] User already exists: {existing_user['id']}")
                return jsonify({"message": "User already exists", "user_id": existing_user['id']}), 200

            # Add user
            user_id = user_model.create_user(firebase_uid, email)
            self.logger.info(f"[/create] New user created with ID: {user_id}")

            return jsonify({"message": "User created successfully", "user_id": user_id}), 201

        except Exception as e:
            self.logger.error(f"[/create] Error occurred while creating user: {str(e)}", exc_info=True)
            return jsonify({"error": "An error occurred while creating the user", "details": str(e)}), 500

        finally:
            self.logger.info("[/create] Closing database connections")
            self.db.close_connections()


# Create controller and blueprint
user_controller = UserController()
user_blueprint = user_controller.blueprint

