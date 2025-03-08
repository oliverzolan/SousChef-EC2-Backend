import logging

class IngredientsModel:
    def __init__(self, db_connection):
        self.db = db_connection

    def get_all_ingredients(self, user_id):
        """
        Fetch all ingredients for a specific user.
        """
        try:
            with self.db.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT foodId, text, quantity, measure, food, weight, foodCategory
                    FROM Ingredients
                    WHERE user_id = %s
                    """,
                    (user_id,)
                )
                ingredients = cursor.fetchall()

            if not ingredients:
                logging.info(f"No ingredients found for user_id {user_id}")
                return {"message": f"No ingredients found for user_id {user_id}"}

            logging.info(f"Fetched {len(ingredients)} ingredients for user_id {user_id}")
            return ingredients

        except Exception as e:
            logging.error(f"Error fetching ingredients for user_id {user_id}: {str(e)}", exc_info=True)
            return {"error": "An error occurred while fetching ingredients", "details": str(e)}

    def add_ingredients_batch(self, user_id, ingredients):
        """
        Batch add ingredients.
        """
        try:
            if not ingredients or not all('foodId' in ing and 'quantity' in ing for ing in ingredients):
                logging.warning(f"Invalid input: {ingredients}")
                return {"error": "Invalid ingredients data. Each ingredient must have 'foodId' and 'quantity'."}

            with self.db.cursor() as cursor:
                logging.info(f"Adding {len(ingredients)} ingredient(s) for user_id {user_id}")

                sql = """
                INSERT INTO Ingredients (user_id, foodId, text, quantity, measure, food, weight, foodCategory)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE quantity = quantity + VALUES(quantity)
                """

                data = [
                    (
                        user_id,
                        ing['foodId'],
                        ing.get('text', ''),
                        ing['quantity'],
                        ing.get('measure', ''),
                        ing.get('food', ''),
                        ing.get('weight', 0),
                        ing.get('foodCategory', '')
                    )
                    for ing in ingredients
                ]

                cursor.executemany(sql, data)
                self.db.commit()

            logging.info(f"Successfully added {len(ingredients)} ingredient(s) for user_id {user_id}")
            return {"message": f"Successfully added {len(ingredients)} ingredient(s)"}

        except Exception as e:
            self.db.rollback()
            logging.error(f"Error adding ingredients for user_id {user_id}: {str(e)}", exc_info=True)
            return {"error": "An error occurred while adding ingredients", "details": str(e)}

    # def remove_ingredients_batch(self, user_id, ingredients):
    #     """
    #     Batch remove ingredients.
    #     """
    #     try:
    #         if not ingredients or not all('foodId' in ing and 'quantity' in ing for ing in ingredients):
    #             logging.warning(f"Invalid input: {ingredients}")
    #             return {"error": "Invalid ingredients data. Each ingredient must have 'foodId' and 'quantity'."}

    #         with self.db.cursor() as cursor:
    #             logging.info(f"Removing {len(ingredients)} ingredient(s) for user_id {user_id}")

    #             for ing in ingredients:
    #                 sql_decrement = """
    #                 UPDATE Ingredients
    #                 SET quantity = quantity - %s
    #                 WHERE user_id = %s AND foodId = %s
    #                 """
    #                 cursor.execute(sql_decrement, (ing['quantity'], user_id, ing['foodId']))

    #                 sql_delete = """
    #                 DELETE FROM Ingredients
    #                 WHERE user_id = %s AND foodId = %s AND quantity <= 0
    #                 """
    #                 cursor.execute(sql_delete, (user_id, ing['foodId']))

    #             self.db.commit()

    #         logging.info(f"Successfully removed {len(ingredients)} ingredient(s) for user_id {user_id}")
    #         return {"message": f"Successfully removed {len(ingredients)} ingredient(s)"}

    #     except Exception as e:
    #         self.db.rollback()
    #         logging.error(f"Error removing ingredients for user_id {user_id}: {str(e)}", exc_info=True)
    #         return {"error": "An error occurred while removing ingredients", "details": str(e)}

    # def update_ingredient_quantity(self, user_id, foodId, quantity_used):
    #     """
    #     Update the quantity of an ingredient when it is used.
    #     """
    #     try:
    #         with self.db.cursor() as cursor:
    #             logging.info(f"Updating ingredient {foodId} for user_id {user_id} by reducing {quantity_used}")

    #             sql_update = """
    #             UPDATE Ingredients
    #             SET quantity = quantity - %s
    #             WHERE user_id = %s AND foodId = %s
    #             """
    #             cursor.execute(sql_update, (quantity_used, user_id, foodId))

    #             sql_delete = """
    #             DELETE FROM Ingredients
    #             WHERE user_id = %s AND foodId = %s AND quantity <= 0
    #             """
    #             cursor.execute(sql_delete, (user_id, foodId))

    #             self.db.commit()

    #         logging.info(f"Successfully updated ingredient {foodId} for user_id {user_id}")
    #         return {"message": f"Successfully updated ingredient {foodId}"}

    #     except Exception as e:
    #         self.db.rollback()
    #         logging.error(f"Error updating ingredient {foodId} for user_id {user_id}: {str(e)}", exc_info=True)
    #         return {"error": "An error occurred while updating ingredient quantity", "details": str(e)}
