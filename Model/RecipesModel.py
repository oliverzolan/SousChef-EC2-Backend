import logging

class RecipesModel:
    def __init__(self, db_connection):
        self.db = db_connection

    def get_all_recipes(self, user_id):
        """
        Fetch all recipes for a specific user.
        """
        try:
            with self.db.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT uri, label, image, url, calories, total_weight, cuisine_type, meal_type, dish_type
                    FROM Recipes
                    WHERE user_id = %s
                    """,
                    (user_id,)
                )
                recipes = cursor.fetchall()

            if not recipes:
                logging.info(f"No recipes found for user_id {user_id}")
                return {"message": f"No recipes found for user_id {user_id}"}

            logging.info(f"Fetched {len(recipes)} recipes for user_id {user_id}")
            return recipes

        except Exception as e:
            logging.error(f"Error fetching recipes for user_id {user_id}: {str(e)}", exc_info=True)
            return {"error": "An error occurred while fetching recipes", "details": str(e)}

    def add_recipe(self, user_id, recipe):
        """
        Add a recipe for a specific user.
        """
        try:
            if not recipe or 'uri' not in recipe:
                logging.warning(f"Invalid input: {recipe}")
                return {"error": "Invalid recipe data. Each recipe must have a 'uri'."}

            with self.db.cursor() as cursor:
                logging.info(f"Adding recipe {recipe['uri']} for user_id {user_id}")

                sql = """
                INSERT IGNORE INTO Recipes (uri, user_id, label, image, url, calories, total_weight, cuisine_type, meal_type, dish_type)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
                """

                data = (
                    recipe['uri'],
                    user_id,
                    recipe['label'],
                    recipe.get('image', ''),
                    recipe.get('url', ''),
                    recipe['calories'],
                    recipe['total_weight'],
                    recipe.get('cuisine_type', ''), 
                    recipe.get('meal_type', ''),
                    recipe.get('dish_type', ''),
                )

                cursor.execute(sql, data)
                self.db.commit()

            logging.info(f"Successfully added recipe {recipe['uri']} for user_id {user_id} (or ignored if duplicate)")
            return {"message": f"Successfully added recipe {recipe['uri']} (or ignored if already exists)"}

        except Exception as e:
            self.db.rollback()
            logging.error(f"Error adding recipe for user_id {user_id}: {str(e)}", exc_info=True)
            return {"error": "An error occurred while adding the recipe", "details": str(e)}

    def delete_recipe(self, user_id, recipe):
        """
        Remove a recipe for a specific user.
        """
        try:
            if not recipe or 'uri' not in recipe:
                logging.warning(f"Invalid input: {recipe}")
                return {"error": "Invalid recipe data. Each recipe must have a 'uri'."}

            with self.db.cursor() as cursor:
                logging.info(f"Removing recipe {recipe['uri']} for user_id {user_id}")

                sql = "DELETE FROM Recipes WHERE uri = %s AND user_id = %s;"
                cursor.execute(sql, (recipe['uri'], user_id))
                self.db.commit()

            logging.info(f"Successfully removed recipe {recipe['uri']} for user_id {user_id}")
            return {"message": f"Successfully removed recipe {recipe['uri']}"}

        except Exception as e:
            self.db.rollback()
            logging.error(f"Error removing recipe {recipe['uri']} for user_id {user_id}: {str(e)}", exc_info=True)
            return {"error": "An error occurred while removing the recipe", "details": str(e)}

