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
                return {"message": "No ingredients found in the database"}

            return ingredients

        except Exception as e:
            # Return an error message to the caller
            return {"error": "An error occurred while fetching ingredients", "details": str(e)}

    def find_ingredient_by_name(self, search_string):
        """
        Check if the input string matches any ingredient names in the database.
        """
        try:
            with self.db.cursor() as cursor:
                # Force case-insensitive matching using COLLATE
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
                return {"message": f"No ingredients found matching '{search_string}'"}

            return results

        except Exception as e:
            # Return an error message to the caller
            return {"error": "An error occurred while searching for ingredients", "details": str(e)}
