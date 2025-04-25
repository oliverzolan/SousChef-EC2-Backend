import logging
from flask import Blueprint, jsonify, request
from Config.Db import Database
from Cache.FbCache import get_cached_uid_redis
from Model.UserIngredientsModel import UserIngredientsModel

class UserIngredientsController:
    """
    Controller with routes, function calling, error handling, and logging.
    """
    def __init__(self):
        self.blueprint = Blueprint('ingredients_blueprint', __name__)
        self.db = Database()

        # Logger setup
        logging.basicConfig(
            filename='/var/log/flask_app.log',
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)

        # Routes
        self.blueprint.add_url_rule('/all', view_func=self.get_all_user_ingredients, methods=['GET'])
        self.blueprint.add_url_rule('/update', view_func=self.update_user_ingredients_batch, methods=['POST'])
        self.blueprint.add_url_rule('/get_expiring', view_func=self.get_expiring_user_ingredients, methods=['GET'])
        self.blueprint.add_url_rule('/delete', view_func=self.delete_user_ingredients_batch, methods=['DELETE'])

    def get_all_user_ingredients(self):
        """
        Fetch all ingredients for a specific user.
        """
        self.logger.info("[/all] Fetching all ingredients")
        connection = None

        try:
            id_token = request.headers.get('Authorization')
            if not id_token:
                self.logger.warning("[/all] Missing Authorization token")
                return jsonify({"error": "Authorization token is missing"}), 401

            user_id = get_cached_uid_redis(id_token)
            if not user_id:
                self.logger.warning("[/all] Invalid or expired token")
                return jsonify({"error": "User ID not found from token"}), 401

            connection = self.db.connect_read()
            ingredients_model = UserIngredientsModel(connection)

            ingredients = ingredients_model.get_all_user_ingredients(user_id)
            if not ingredients:
                self.logger.info(f"[/all/{user_id}] No ingredients found")
                return jsonify({"message": "No ingredients found"}), 404

            self.logger.info(f"[/all/{user_id}] Retrieved {len(ingredients)} ingredients")
            return jsonify(ingredients), 200

        except Exception as e:
            self.logger.error(f"[/all] Error: {str(e)}", exc_info=True)
            return jsonify({"error": "An error occurred", "details": str(e)}), 500

        finally:
            if connection:
                connection.close()
            self.logger.info("[/all] Database connection closed")

    def update_user_ingredients_batch(self):
        """
        Batch update ingredients for the user.
        """
        self.logger.info("[/update] Updating ingredients batch")
        connection = None

        try:
            data = request.json
            ingredients = data.get("ingredients")

            if not ingredients:
                self.logger.warning("[/update] Missing ingredients payload")
                return jsonify({"error": "Missing ingredients"}), 400

            id_token = request.headers.get('Authorization')
            if not id_token:
                self.logger.warning("[/update] Missing Authorization token")
                return jsonify({"error": "Authorization token is missing"}), 401

            user_id = get_cached_uid_redis(id_token)
            if not user_id:
                self.logger.warning("[/update] Invalid or expired token")
                return jsonify({"error": "User ID not found from token"}), 401

            connection = self.db.connect_write()
            ingredients_model = UserIngredientsModel(connection)

            response = ingredients_model.update_user_ingredients_batch(user_id, ingredients)
            return jsonify(response), 200

        except Exception as e:
            self.logger.error(f"[/update] Error: {str(e)}", exc_info=True)
            return jsonify({"error": "An error occurred", "details": str(e)}), 500

        finally:
            if connection:
                connection.close()
            self.logger.info("[/update] Database connection closed")

    def get_expiring_user_ingredients(self):
        """
        Fetch all expiring ingredients for a specific user within 24 hours.
        """
        self.logger.info("[/get_expring] Fetching all ingredients")
        connection = None

        try:
            id_token = request.headers.get('Authorization')
            if not id_token:
                self.logger.warning("[/get_expring] Missing Authorization token")
                return jsonify({"error": "Authorization token is missing"}), 401

            user_id = get_cached_uid_redis(id_token)
            if not user_id:
                self.logger.warning("[/get_expring] Invalid or expired token")
                return jsonify({"error": "User ID not found from token"}), 401

            connection = self.db.connect_read()
            ingredients_model = UserIngredientsModel(connection)

            ingredients = ingredients_model.get_ingredients_expiring(user_id)
            if not ingredients:
                self.logger.info(f"[/get_expring/{user_id}] No ingredients found")
                return jsonify({"message": "No ingredients found"}), 404

            self.logger.info(f"[/get_expring/{user_id}] Retrieved {len(ingredients)} ingredients")
            return jsonify(ingredients), 200

        except Exception as e:
            self.logger.error(f"[/get_expring] Error: {str(e)}", exc_info=True)
            return jsonify({"error": "An error occurred", "details": str(e)}), 500

        finally:
            if connection:
                connection.close()
            self.logger.info("[/get_expring] Database connection closed")

    def delete_user_ingredients_batch(self):
        """
        Batch delete ingredients for the user.
        """
        self.logger.info("[/delete] Deleting ingredients batch")
        connection = None

        try:
            data = request.json
            edamam_food_id = data.get("edamam_food_id")

            if not edamam_food_id:
                self.logger.warning("[/delete] Missing edamam_food_id payload")
                return jsonify({"error": "Missing edamam_food_id"}), 400

            if isinstance(edamam_food_id, str):
                edamam_food_id = [edamam_food_id]

            id_token = request.headers.get('Authorization')
            if not id_token:
                self.logger.warning("[/delete] Missing Authorization token")
                return jsonify({"error": "Authorization token is missing"}), 401

            user_id = get_cached_uid_redis(id_token)
            if not user_id:
                self.logger.warning("[/delete] Invalid or expired token")
                return jsonify({"error": "User ID not found from token"}), 401

            connection = self.db.connect_write()
            ingredients_model = UserIngredientsModel(connection)

            response = ingredients_model.delete_user_ingredients_batch(user_id, edamam_food_id)
            return jsonify(response), 200

        except Exception as e:
            self.logger.error(f"[/delete] Error: {str(e)}", exc_info=True)
            return jsonify({"error": "An error occurred", "details": str(e)}), 500

        finally:
            if connection:
                connection.close()



# Register controller and blueprint
user_ingredients_controller = UserIngredientsController()
user_ingredients_blueprint = user_ingredients_controller.blueprint
