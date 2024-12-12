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
        self.blueprint.add_url_rule('/all', view_func=self.get_all_ingredients, methods=['GET'])
        self.blueprint.add_url_rule('/search', view_func=self.search_ingredients, methods=['GET'])

    def get_all_ingredients(self):
        """
        Fetch all ingredients.
        """
        self.logger.info("[/all] Fetching all ingredients")
        try:
            # Establish database connection
            connection = self.db.connect_read()
            ingredients_model = IngredientsModel(connection)

            # Get Ingredients
            ingredients = ingredients_model.get_all_ingredients()
            if not ingredients:
                self.logger.info("[/all] No ingredients found")
                return jsonify({"message": "No ingredients found"}), 404

            self.logger.info(f"[/all] Retrieved {len(ingredients)} ingredients")
            return jsonify(ingredients), 200

        except Exception as e:
            self.logger.error(f"[/all] Error occurred: {str(e)}", exc_info=True)
            return jsonify({"error": "An error occurred while fetching ingredients", "details": str(e)}), 500

        finally:
            self.logger.info("[/all] Closing database connections")
            self.db.close_connections()

    def search_ingredients(self):
        """
        Search for ingredients by name.
        """
        self.logger.info("[/search] Searching for ingredients")
        try:
            # Get query parameters
            search_string = request.args.get('query', '').strip()
            if not search_string:
                self.logger.warning("[/search] Query parameter 'query' is missing")
                return jsonify({"error": "Query parameter 'query' is required"}), 400

            # Establish a database connection
            connection = self.db.connect_read()
            ingredients_model = IngredientsModel(connection)

            # Get Ingredients
            results = ingredients_model.find_ingredient_by_name(search_string)
            if "message" in results:
                self.logger.info(f"[/search] No ingredients found for query: {search_string}")
                return jsonify(results), 404

            self.logger.info(f"[/search] Found {len(results)} ingredients for query: {search_string}")
            return jsonify(results), 200

        except Exception as e:
            self.logger.error(f"[/search] Error occurred: {str(e)}", exc_info=True)
            return jsonify({"error": "An error occurred while searching for ingredients", "details": str(e)}), 500

        finally:
            self.logger.info("[/search] Closing database connections")
            self.db.close_connections()


# Create controller and blueprint
ingredients_controller = IngredientsController()
ingredients_blueprint = ingredients_controller.blueprint
