import logging

class IngredientsModel:
    def __init__(self, db_connection):
        self.db = db_connection

    def get_all_ingredients(self):
        """
        Fetch all ingredients from the Ingredients table.
        """
        try:
            with self.db.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT ingredient_id, name, description, category
                    FROM Ingredients
                    """
                )
                ingredients = cursor.fetchall()

            if not ingredients:
                logging.info("No ingredients found in the database")
                return {"message": "No ingredients found in the database"}

            logging.info(f"Fetched {len(ingredients)} ingredients from the database")
            return ingredients

        except Exception as e:
            logging.error(f"Error fetching ingredients: {str(e)}", exc_info=True)
            return {"error": "An error occurred while fetching ingredients", "details": str(e)}

    def find_ingredient_by_name(self, search_string):
        """
        Search for ingredients by name in the Ingredients table.
        """
        try:
            with self.db.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT ingredient_id, name, description, category
                    FROM Ingredients
                    WHERE name LIKE %s COLLATE utf8_general_ci
                    """,
                    (f"%{search_string}%",)
                )
                results = cursor.fetchall()

            if not results:
                logging.info(f"No ingredients found matching '{search_string}'")
                return {"message": f"No ingredients found matching '{search_string}'"}

            logging.info(f"Found {len(results)} ingredients matching '{search_string}'")
            return results

        except Exception as e:
            logging.error(f"Error searching for ingredients with query '{search_string}': {str(e)}", exc_info=True)
            return {"error": "An error occurred while searching for ingredients", "details": str(e)}
