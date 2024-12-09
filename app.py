from flask import Flask
from Controller.PantryController import pantry_blueprint
from Controller.RecipeController import recipe_blueprint
from Controller.UserController import user_blueprint
from Config.Fb import initialize_firebase

app = Flask(__name__)

initialize_firebase()

# Register Blueprints
app.register_blueprint(pantry_blueprint, url_prefix='/pantry')
app.register_blueprint(recipe_blueprint, url_prefix='/recipes')
app.register_blueprint(user_blueprint, url_prefix='/users')

print(app.url_map)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
