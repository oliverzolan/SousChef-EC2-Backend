import logging
from flask import Blueprint, jsonify, request
from Config.Db import Database
from Config.Fb import verify_firebase_token
from Cache.FbCache import get_cached_uid_redis
from Model.PantryModel import PantryModel
from Model.UserModel import UserModel


class PantryController:
    def __init__(self):
        self.blueprint = Blueprint('pantry_blueprint', __name__)
        self.db = Database()

        # Initialize logger for the class
        self.logger = logging.getLogger(self.__class__.__name__)
        logging.basicConfig(
            filename='/var/log/flask_app.log',
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )

        # Register routes
        self.blueprint.add_url_rule('/user', view_func=self.get_user_pantry, methods=['GET'])
        self.blueprint.add_url_rule('/user/add-ingredients', view_func=self.add_ingredients_to_pantry, methods=['POST'])

    def get_user_pantry(self):
        """
        Fetch all pantry items for the authenticated user based on Firebase token.
        """
        self.logger.info("Processing /user pantry request")
        try:
            id_token = request.headers.get('Authorization')
            if not id_token:
                self.logger.warning("Authorization token is missing in the request")
                return jsonify({"error": "Authorization token is missing"}), 401

            # Verify and cache the Firebase UID
            firebase_uid = get_cached_uid_redis(id_token)
            if not firebase_uid:
                self.logger.warning("Invalid or expired Firebase token")
                return jsonify({"error": "Invalid or expired Firebase token"}), 401

            # Initialize database connections and models
            connection = self.db.connect_read()
            user_model = UserModel(connection)
            pantry_model = PantryModel(connection)

            # Get the user ID based on Firebase UID
            user = user_model.get_user_by_firebase_uid(firebase_uid)
            if not user:
                self.logger.warning(f"User not found for Firebase UID: {firebase_uid}")
                return jsonify({"error": "User not found"}), 404

            user_id = user['id']
            self.logger.info(f"Fetched user ID: {user_id} for a verified Firebase UID")

            # Get pantry items for the user
            pantry_items = pantry_model.get_pantry_items_by_user_id(user_id)
            if not pantry_items:
                self.logger.info(f"No pantry items found for user ID: {user_id}")
                return jsonify({"message": "No pantry items found for this user"}), 404

            self.logger.info(f"Pantry items fetched for user ID: {user_id}")
            return jsonify(pantry_items), 200

        except Exception as e:
            self.logger.error(f"Error occurred while fetching pantry items: {str(e)}", exc_info=True)
            return jsonify({"error": "An error occurred while fetching pantry items", "details": str(e)}), 500

        finally:
            self.logger.info("Closing database connections for /user pantry request")
            self.db.close_connections()

    def add_ingredients_to_pantry(self):
        """
        Batch add ingredients to the pantry for the authenticated user based on Firebase token.
        """
        self.logger.info("Processing /user/add-ingredients request")
        try:
            id_token = request.headers.get('Authorization')
            if not id_token:
                self.logger.warning("Authorization token is missing in the request")
                return jsonify({"error": "Authorization token is missing"}), 401

            # Verify and cache the Firebase UID
            firebase_uid = get_cached_uid_redis(id_token)
            if not firebase_uid:
                self.logger.warning("Invalid or expired Firebase token")
                return jsonify({"error": "Invalid or expired Firebase token"}), 401

            # Initialize database connections and models
            connection = self.db.connect_write()
            user_model = UserModel(connection)
            pantry_model = PantryModel(connection)

            # Get the user ID based on Firebase UID
            user = user_model.get_user_by_firebase_uid(firebase_uid)
            if not user:
                self.logger.warning(f"User not found for Firebase UID: {firebase_uid}")
                return jsonify({"error": "User not found"}), 404

            user_id = user['id']
            self.logger.info(f"Fetched user ID: {user_id} for a verified Firebase UID")

            # Get the batch of ingredients from the request body
            ingredients = request.json.get('ingredients', [])
            if not ingredients:
                self.logger.warning("No ingredients provided in the request body")
                return jsonify({"error": "No ingredients provided"}), 400

            # Add ingredients to the pantry
            result = pantry_model.add_ingredients_batch(user_id, ingredients)
            if "error" in result:
                self.logger.error(f"Failed to add ingredients for user ID: {user_id}")
                return jsonify(result), 500

            self.logger.info(f"Successfully added ingredients to the pantry for user ID: {user_id}")
            return jsonify({"message": "Ingredients added successfully", "details": result}), 201

        except Exception as e:
            self.logger.error(f"Error occurred while adding ingredients: {str(e)}", exc_info=True)
            return jsonify({"error": "An error occurred while adding ingredients", "details": str(e)}), 500

        finally:
            self.logger.info("Closing database connections for /user/add-ingredients request")
            self.db.close_connections()


# Create an instance for Controller and blueprint
pantry_controller = PantryController()
pantry_blueprint = pantry_controller.blueprint
