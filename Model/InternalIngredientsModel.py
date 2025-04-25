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

    def get_nutrition_by_edamam_id(self, edamam_id):
        """
        Fetch nutrition details for an ingredient by ID.
        """
        try:
            with self.db.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT 
                        Edamam_Food_ID, Name, Category, Quantity_Type, Quantity,
                        Fat, Cholesterol, Sodium, Potassium,
                        Carbohydrate, Protein, Calorie
                    FROM InternalIngredients
                    WHERE Edamam_Food_ID = %s
                    """,
                    (edamam_id,)
                )
                result = cursor.fetchone()

            if not result:
                logging.info(f"No nutrition info found for Edamam_Food_ID: {edamam_id}")
                return {"message": f"No nutrition info found for food ID: {edamam_id}"}

            logging.info(f"Nutrition info found for Edamam_Food_ID: {edamam_id}")
            return result

        except Exception as e:
            logging.error(f"Error fetching nutrition info for Edamam_Food_ID '{edamam_id}': {str(e)}", exc_info=True)
            return {"error": "An error occurred while fetching nutrition info", "details": str(e)}


