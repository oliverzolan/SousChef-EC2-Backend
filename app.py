import os
from dotenv import load_dotenv
from flask import Flask
from Controller.IngredientsController import ingredients_blueprint
from Controller.PantryController import pantry_blueprint
from Controller.RecipeController import recipe_blueprint
from Controller.UserController import user_blueprint
from Config.Fb import initialize_firebase

def create_app():
    app = Flask(__name__)

    initialize_firebase()

    app.register_blueprint(pantry_blueprint, url_prefix='/pantry')
    app.register_blueprint(recipe_blueprint, url_prefix='/recipes')
    app.register_blueprint(user_blueprint, url_prefix='/users')
    app.register_blueprint(ingredients_blueprint, url_prefix='/ingredients')

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(
        host="0.0.0.0",
        port=5000,
        ssl_context=(
            os.getenv("SSL_CERT_PATH"),
            os.getenv("SSL_KEY_PATH")
        )
    )

