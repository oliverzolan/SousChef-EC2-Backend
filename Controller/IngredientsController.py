from flask import Blueprint, jsonify, request
from Config.Db import Database
from Model.IngredientsModel import IngredientsModel

ingredients_blueprint = Blueprint('ingredients_blueprint', __name__)
db = Database()

@ingredients_blueprint.route('/all', methods=['GET'])
def get_all_ingredients():
    """
    Fetch all ingredients from the database.
    """
    try:
        # Establish a database connection
        connection = db.connect_read()
        ingredients_model = IngredientsModel(connection)

        # Fetch all ingredients
        ingredients = ingredients_model.get_all_ingredients()
        if not ingredients:
            return jsonify({"message": "No ingredients found"}), 404

        return jsonify(ingredients), 200

    except Exception as e:
        return jsonify({"error": "An error occurred while fetching ingredients", "details": str(e)}), 500

    finally:
        db.close_connections()

@ingredients_blueprint.route('/search', methods=['GET'])
def search_ingredients():
    """
    Search for ingredients by name.
    """
    try:
        # Get the search string from the query parameters
        search_string = request.args.get('query', '').strip()
        if not search_string:
            return jsonify({"error": "Query parameter 'query' is required"}), 400

        # Establish a database connection
        connection = db.connect_read()
        ingredients_model = IngredientsModel(connection)

        # Search for ingredients by name
        results = ingredients_model.find_ingredient_by_name(search_string)
        if "message" in results:
            return jsonify(results), 404

        return jsonify(results), 200

    except Exception as e:
        return jsonify({"error": "An error occurred while searching for ingredients", "details": str(e)}), 500

    finally:
        db.close_connections()