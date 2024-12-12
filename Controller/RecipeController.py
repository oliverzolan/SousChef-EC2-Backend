from flask import Blueprint, jsonify
import logging

class RecipeController:
    """
    Controller with routes, function calling, error handling, and logging.
    """
    def __init__(self):
        self.blueprint = Blueprint('recipe', __name__)

        # Initialize the logger
        logging.basicConfig(
            filename='/var/log/flask_app.log', 
            level=logging.INFO,               
            format='%(asctime)s - %(levelname)s - %(message)s' 
        )
        self.logger = logging.getLogger(__name__)  

        # Routes
        self.blueprint.add_url_rule('/dummy', view_func=self.dummy_route, methods=['GET'])

    def dummy_route(self):
        """
        Dummy route.
        """
        try:
            self.logger.info("Accessed dummy route successfully.") 
            response = {"message": "This is a dummy route"}
            self.logger.info(f"Response: {response}")  
            return jsonify(response), 200
        except Exception as e:
            error_response = {"error": "An error occurred", "details": str(e)}
            self.logger.error(f"Error in dummy route: {error_response}")  
            return jsonify(error_response), 500


# Create controller and blueprint
recipe_controller = RecipeController()
recipe_blueprint = recipe_controller.blueprint
