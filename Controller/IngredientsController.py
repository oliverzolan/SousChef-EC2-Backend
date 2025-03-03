import logging
from flask import Blueprint, jsonify, request
from Config.Db import Database
from Model.IngredientsModel import IngredientsModel

class IngredientsController:
    """
    Controller with routes, function calling, error handling, and logging.
    """
    def __init__(self):
        self.blueprint = Blueprint('ingredients_blueprint', __name__)
        self.db = Database()

        # Initialize logger
        logging.basicConfig(
            filename='/var/log/flask_app.log', 
            level=logging.INFO,                
            format='%(asctime)s - %(levelname)s - %(message)s'  
        )
        self.logger = logging.getLogger(__name__)

        # Routes
        self.blueprint.add_url_rule('/all/<int:user_id>', view_func=self.get_all_ingredients, methods=['GET'])
        self.blueprint.add_url_rule('/add', view_func=self.add_ingredients_batch, methods=['POST'])
        self.blueprint.add_url_rule('/remove', view_func=self.remove_ingredients_batch, methods=['POST'])
        self.blueprint.add_url_rule('/update', view_func=self.update_ingredient_quantity, methods=['POST'])

    def get_all_ingredients(self, user_id):
        """
        Fetch all ingredients for a specific user.
        """
        self.logger.info(f"[/all/{user_id}] Fetching all ingredients")
        try:
            connection = self.db.connect_read()
            ingredients_model = IngredientsModel(connection)

            ingredients = ingredients_model.get_all_ingredients(user_id)
            if not ingredients:
                self.logger.info(f"[/all/{user_id}] No ingredients found")
                return jsonify({"message": "No ingredients found"}), 404

            self.logger.info(f"[/all/{user_id}] Retrieved {len(ingredients)} ingredients")
            return jsonify(ingredients), 200

        except Exception as e:
            self.logger.error(f"[/all/{user_id}] Error occurred: {str(e)}", exc_info=True)
            return jsonify({"error": "An error occurred while fetching ingredients", "details": str(e)}), 500

        finally:
            self.logger.info(f"[/all/{user_id}] Closing database connection")
            self.db.close_connections()

    def add_ingredients_batch(self):
        """
        Batch add ingredients.
        """
        try:
            data = request.json
            user_id = data.get("user_id")
            ingredients = data.get("ingredients")

            if not user_id or not ingredients:
                self.logger.warning("[/add] Missing user_id or ingredients data")
                return jsonify({"error": "Missing user_id or ingredients"}), 400

            connection = self.db.connect_write()
            ingredients_model = IngredientsModel(connection)

            response = ingredients_model.add_ingredients_batch(user_id, ingredients)
            return jsonify(response), 200

        except Exception as e:
            self.logger.error(f"[/add] Error adding ingredients: {str(e)}", exc_info=True)
            return jsonify({"error": "An error occurred while adding ingredients", "details": str(e)}), 500

        finally:
            self.logger.info("[/add] Closing database connection")
            self.db.close_connections()

    def remove_ingredients_batch(self):
        """
        Batch remove ingredients.
        """
        try:
            data = request.json
            user_id = data.get("user_id")
            ingredients = data.get("ingredients")

            if not user_id or not ingredients:
                self.logger.warning("[/remove] Missing user_id or ingredients data")
                return jsonify({"error": "Missing user_id or ingredients"}), 400

            connection = self.db.connect_write()
            ingredients_model = IngredientsModel(connection)

            response = ingredients_model.remove_ingredients_batch(user_id, ingredients)
            return jsonify(response), 200

        except Exception as e:
            self.logger.error(f"[/remove] Error removing ingredients: {str(e)}", exc_info=True)
            return jsonify({"error": "An error occurred while removing ingredients", "details": str(e)}), 500

        finally:
            self.logger.info("[/remove] Closing database connection")
            self.db.close_connections()

    def update_ingredient_quantity(self):
        """
        Update ingredient quantity when an ingredient is used.
        """
        try:
            data = request.json
            user_id = data.get("user_id")
            foodId = data.get("foodId")
            quantity_used = data.get("quantity_used")

            if not user_id or not foodId or quantity_used is None:
                self.logger.warning("[/update] Missing required data")
                return jsonify({"error": "Missing user_id, foodId, or quantity_used"}), 400

            connection = self.db.connect_write()
            ingredients_model = IngredientsModel(connection)

            response = ingredients_model.update_ingredient_quantity(user_id, foodId, quantity_used)
            return jsonify(response), 200

        except Exception as e:
            self.logger.error(f"[/update] Error updating ingredient quantity: {str(e)}", exc_info=True)
            return jsonify({"error": "An error occurred while updating ingredient quantity", "details": str(e)}), 500

        finally:
            self.logger.info("[/update] Closing database connection")
            self.db.close_connections()

# Create controller and blueprint
ingredients_controller = IngredientsController()
ingredients_blueprint = ingredients_controller.blueprint
