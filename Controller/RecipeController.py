from flask import Blueprint, jsonify
import logging

# Define the blueprint
recipe_blueprint = Blueprint('recipe', __name__)

# Initialize the logger
logging.basicConfig(
    filename='/var/log/flask_app.log',  # Log file path
    level=logging.INFO,                # Logging level
    format='%(asctime)s - %(levelname)s - %(message)s'  # Log format
)
logger = logging.getLogger(__name__)  # Logger instance for the blueprint

# Create a dummy route
@recipe_blueprint.route('/dummy', methods=['GET'])
def dummy_route():
    try:
        logger.info("Accessed dummy route successfully.")  # Log the success
        response = {"message": "This is a dummy route"}
        logger.info(f"Response: {response}")  # Log the response
        return jsonify(response), 200
    except Exception as e:
        error_response = {"error": "An error occurred", "details": str(e)}
        logger.error(f"Error in dummy route: {error_response}")  # Log any errors
        return jsonify(error_response), 500