from flask import Blueprint, jsonify, request
from Config.Db import Database
from Config.Fb import verify_firebase_token
from Cache.FbCache import get_cached_uid_redis
from Model.RecipesModel import RecipesModel  
import logging

class RecipeController:
    """
    Controller with routes, function calling, error handling, and logging.
    """
    def __init__(self):
        self.blueprint = Blueprint('recipe_blueprint', __name__)
        self.db = Database()  # Added database connection

        # Initialize logger
        logging.basicConfig(
            filename='/var/log/flask_app.log', 
            level=logging.INFO,               
            format='%(asctime)s - %(levelname)s - %(message)s' 
        )
        self.logger = logging.getLogger(__name__)  

        # Routes
        self.blueprint.add_url_rule('/all', view_func=self.get_all_recipes, methods=['GET'])
        self.blueprint.add_url_rule('/add', view_func=self.add_saved_recipes, methods=['POST'])
        self.blueprint.add_url_rule('/remove', view_func=self.removed_saved_recipes, methods=['POST'])

    def get_all_recipes(self):
        """
        Fetch all recipes for a specific user.
        """
        self.logger.info(f"[/all] Fetching all recipes")
        try:
            # Get Authorization token
            id_token = request.headers.get('Authorization')
            if not id_token:
                self.logger.warning("Authorization token is missing in the request")
                return jsonify({"error": "Authorization token is missing"}), 401

            # Get user ID from token
            user_id = get_cached_uid_redis(id_token)
            if not user_id:
                self.logger.warning(f"User ID not found for token: {id_token}")
                return jsonify({"error": "User ID not found from Token"}), 401

            connection = self.db.connect_read()
            recipe_model = RecipesModel(connection)

            recipes = recipe_model.get_all_recipes(user_id)
            if not recipes:
                self.logger.info(f"[/all/] No recipes found")
                return jsonify({"message": "No recipes found"}), 404

            self.logger.info(f"[/all/{user_id}] Retrieved {len(recipes)} recipes")
            return jsonify(recipes), 200

        except Exception as e:
            self.logger.error(f"[/all] Error occurred: {str(e)}", exc_info=True)
            return jsonify({"error": "An error occurred while fetching recipes", "details": str(e)}), 500

    def add_saved_recipes(self):
        """
        Add recipes.
        """
        try:
            data = request.json
            recipe = data.get("recipe")

            if not recipe:
                self.logger.warning("[/add] Missing Recipe parameters")
                return jsonify({"error": "Missing Recipe"}), 400

            # Get Authorization token
            id_token = request.headers.get('Authorization')
            if not id_token:
                self.logger.warning("Authorization token is missing in the request")
                return jsonify({"error": "Authorization token is missing"}), 401

            # Get user ID
            user_id = get_cached_uid_redis(id_token)
            if not user_id:
                self.logger.warning(f"User ID not found for token: {id_token}")
                return jsonify({"error": "User ID not found from Token"}), 401

            connection = self.db.connect_write()
            recipe_model = RecipesModel(connection)

            response = recipe_model.add_recipe(user_id, recipe)
            return jsonify(response), 200

        except Exception as e:
            self.logger.error(f"[/add] Error adding recipe: {str(e)}", exc_info=True)
            return jsonify({"error": "An error occurred while adding recipe", "details": str(e)}), 500

    def removed_saved_recipes(self):
        """
        Remove recipe.
        """
        try:
            data = request.json
            recipe = data.get("recipe") 

            if not recipe:
                self.logger.warning("[/remove] Missing Recipe data")
                return jsonify({"error": "Missing Recipe"}), 400

            # Get Authorization token
            id_token = request.headers.get('Authorization')
            if not id_token:
                self.logger.warning("Authorization token is missing in the request")
                return jsonify({"error": "Authorization token is missing"}), 401

            # Get user ID
            user_id = get_cached_uid_redis(id_token)
            if not user_id:
                self.logger.warning(f"User ID not found for token: {id_token}")
                return jsonify({"error": "User ID not found from Token"}), 401

            connection = self.db.connect_write()
            recipe_model = RecipesModel(connection)

            response = recipe_model.delete_recipe(user_id, recipe) 
            return jsonify(response), 200

        except Exception as e:
            self.db.rollback()
            self.logger.error(f"[/remove] Error removing recipe: {str(e)}", exc_info=True)
            return jsonify({"error": "An error occurred while removing recipe", "details": str(e)}), 500

# Create controller and blueprint
recipes_controller = RecipeController()
recipes_blueprint = recipes_controller.blueprint