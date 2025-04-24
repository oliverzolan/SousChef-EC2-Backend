import logging

class InternalIngredientsModel:
    def __init__(self, db_connection):
        self.db = db_connection

    def get_all_ingredients(self, q, limit):
        """
        Fetch internal ingredients by name search and limit.
        """
        try:
            with self.db.cursor() as cursor:
                search_term = q.lower()
                cursor.execute(
                    """
                    SELECT Edamam_Food_ID, Name, Category, Quantity_Type, Expiration_Duration, Image_URL
                    FROM InternalIngredients
                    WHERE LOWER(Name) LIKE %s
                    ORDER BY 
                        CASE 
                            WHEN LOWER(Name) LIKE %s THEN 1
                            ELSE 2
                        END,
                        Name ASC
                    LIMIT %s
                    """,
                    (f"%{search_term}%", f"{search_term}%", int(limit))
                )
                ingredients = cursor.fetchall()

            if not ingredients:
                logging.info(f"No ingredients found for query: {q}")
                return {"message": f"No ingredients found for query: {q}"}

            logging.info(f"Found {len(ingredients)} ingredients for query: {q}")
            return ingredients

        except Exception as e:
            logging.error(f"Error searching ingredients with query '{q}': {str(e)}", exc_info=True)
            return {"error": "An error occurred while searching for ingredients", "details": str(e)}
