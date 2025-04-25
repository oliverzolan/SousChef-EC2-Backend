import os
from dotenv import load_dotenv
from flask import Flask
from firebase_admin import credentials, auth
# from Controller.PantryController import pantry_blueprint
from Controller.UserIngredientsController import user_ingredients_blueprint
from Controller.InternalIngredientsController import internal_ingredients_blueprint
from Controller.ReportsController import reports_blueprint
from Controller.RecipeController import recipes_blueprint
from Controller.UserController import user_blueprint

from Config.Fb import initialize_firebase


load_dotenv()

app = Flask(__name__)

initialize_firebase()

# app.register_blueprint(pantry_blueprint, url_prefix='/pantry')
app.register_blueprint(recipes_blueprint, url_prefix='/recipes')
app.register_blueprint(user_blueprint, url_prefix='/users')
app.register_blueprint(user_ingredients_blueprint, url_prefix='/user_ingredients')
app.register_blueprint(internal_ingredients_blueprint, url_prefix='/internal_ingredients')
app.register_blueprint(reports_blueprint, url_prefix='/reports')

# Setup for python3
if __name__ == '__main__':
    app.run(
        host="0.0.0.0",
        port=5000,
        ssl_context=(
            os.getenv("SSL_CERT_PATH"),
            os.getenv("SSL_KEY_PATH")
        )
    )

