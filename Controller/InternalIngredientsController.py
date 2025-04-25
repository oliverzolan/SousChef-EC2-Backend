import logging
from flask import Blueprint, jsonify, request
from Config.Db import Database
from Model.InternalIngredientsModel import InternalIngredientsModel

class InternalIngredientsController:
    """
    Controller with routes, function calling, error handling, and logging.
    """
    def __init__(self):
        self.blueprint = Blueprint('internal_ingredients_blueprint', __name__)
        self.db = Database()

        # Initialize logger
        logging.basicConfig(
            filename='/var/log/flask_app.log',
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)

        # Routes
        self.blueprint.add_url_rule('/search', view_func=self.get_ingredients_with_search, methods=['GET'])
        self.blueprint.add_url_rule('/get_nutirtion_by_id', view_func=self.get_nutrition_by_id, methods=['GET'])


    def get_ingredients_with_search(self):
        """
        Fetch ingredients by name search with limit.
        """
        self.logger.info("[/search] Fetching ingredients by search")

        connection = None
        try:
            q = request.args.get("q")
            limit = request.args.get("limit")

            if not q or limit is None:
                self.logger.warning("[/search] Missing query parameters")
                return jsonify({"error": "Missing 'q' or 'limit' parameters"}), 400

            connection = self.db.connect_read()
            internal_ingredients_model = InternalIngredientsModel(connection)

            ingredients = internal_ingredients_model.get_all_ingredients(q, limit)

            if not ingredients:
                self.logger.info("[/search] No ingredients found")
                return jsonify({"message": "No ingredients found"}), 404

            self.logger.info(f"[/search] Retrieved {len(ingredients)} ingredients")
            return jsonify(ingredients), 200

        except Exception as e:
            self.logger.error(f"[/search] Error occurred: {str(e)}", exc_info=True)
            return jsonify({
                "error": "An error occurred while fetching ingredients",
                "details": str(e)
            }), 500

        finally:
            if connection:
                connection.close()
            self.logger.info("[/search] Database connection closed")

    def get_nutrition_by_id(self):
        """
        Fetch  nutrition by Edamam Food ID.
        """
        self.logger.info("[/get_nutrition_by_id] Fetching nutrition info")

        connection = None
        try:
            food_id = request.args.get("edamam_food_id")
            if not food_id:
                self.logger.warning("[/get_nutrition_by_id] Missing 'edamam_food_id' parameter")
                return jsonify({"error": "Missing 'edamam_food_id' parameter"}), 400

            connection = self.db.connect_read()
            internal_ingredients_model = InternalIngredientsModel(connection)

            nutrition = internal_ingredients_model.get_nutrition_by_edamam_id(food_id)

            if not nutrition or isinstance(nutrition, dict) and "message" in nutrition:
                self.logger.info(f"[/get_nutrition_by_id] No data found for food ID: {food_id}")
                return jsonify({"message": "No nutrition info found"}), 404

            self.logger.info(f"[/get_nutrition_by_id] Nutrition info found for {food_id}")
            return jsonify(nutrition), 200

        except Exception as e:
            self.logger.error(f"[/get_nutrition_by_id] Error: {str(e)}", exc_info=True)
            return jsonify({
                "error": "An error occurred while fetching nutrition info",
                "details": str(e)
            }), 500

        finally:
            if connection:
                connection.close()
            self.logger.info("[/get_nutrition_by_id] Database connection closed")


# Blueprint to register
internal_ingredients_controller = InternalIngredientsController()
internal_ingredients_blueprint = internal_ingredients_controller.blueprint
