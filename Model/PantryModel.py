import logging

class PantryModel:
    def __init__(self, db_connection):
        self.db = db_connection

    def get_pantry_items_by_user_id(self, user_id):
        """
        Fetch all pantry items for a given user ID.
        """
        try:
            with self.db.cursor() as cursor:
                logging.info(f"Fetching pantry items for user_id {user_id}")
                cursor.execute(
                    """
                    SELECT Pantry.id, Pantry.ingredient_id, Pantry.quantity, Pantry.added_at, Ingredients.name AS ingredient_name
                    FROM Pantry
                    JOIN Ingredients ON Pantry.ingredient_id = Ingredients.ingredient_id
                    WHERE Pantry.user_id = %s
                    """,
                    (user_id,)
                )
                pantry_items = cursor.fetchall()

            if not pantry_items:
                logging.info(f"No pantry items found for user_id {user_id}")
                return {"message": "User has no items in their pantry"}

            logging.info(f"Successfully fetched {len(pantry_items)} pantry item(s) for user_id {user_id}")
            return pantry_items

        except Exception as e:
            logging.error(f"Error fetching pantry items for user_id {user_id}: {str(e)}", exc_info=True)
            return {"error": "An error occurred while fetching pantry items", "details": str(e)}

    def add_ingredients_batch(self, user_id, ingredients):
        """
        Batch add ingredients to the pantry for a given user ID.

        Args:
            user_id (int): The ID of the user.
            ingredients (list): List of dictionaries with 'ingredient_id' and 'quantity'.

        Returns:
            dict: Success or error message.
        """
        try:
            if not ingredients or not all('ingredient_id' in ing and 'quantity' in ing for ing in ingredients):
                logging.warning(f"Invalid input: {ingredients}")
                return {"error": "Invalid ingredients data. Each ingredient must have 'ingredient_id' and 'quantity'."}

            with self.db.cursor() as cursor:
                logging.info(f"Adding {len(ingredients)} ingredient(s) to the pantry for user_id {user_id}")
                sql = """
                INSERT INTO Pantry (user_id, ingredient_id, quantity, added_at)
                VALUES (%s, %s, %s, NOW())
                ON DUPLICATE KEY UPDATE quantity = quantity + VALUES(quantity)
                """
                data = [(user_id, ing['ingredient_id'], ing['quantity']) for ing in ingredients]
                cursor.executemany(sql, data)
                self.db.commit()

            logging.info(f"Successfully added {len(ingredients)} ingredient(s) to the pantry for user_id {user_id}")
            return {"message": f"Successfully added {len(ingredients)} ingredient(s) to the pantry"}

        except Exception as e:
            self.db.rollback()
            logging.error(f"Error adding ingredients to the pantry for user_id {user_id}: {str(e)}", exc_info=True)
            return {"error": "An error occurred while adding ingredients to the pantry", "details": str(e)}

    def remove_ingredients_batch(self, user_id, ingredients):
        """
        Batch remove ingredients from the pantry for a given user ID.

        Args:
            user_id (int): The ID of the user.
            ingredients (list): List of dictionaries with 'ingredient_id' and 'quantity'.

        Returns:
            dict: Success or error message.
        """
        try:
            if not ingredients or not all('ingredient_id' in ing and 'quantity' in ing for ing in ingredients):
                logging.warning(f"Invalid input: {ingredients}")
                return {"error": "Invalid ingredients data. Each ingredient must have 'ingredient_id' and 'quantity'."}

            with self.db.cursor() as cursor:
                logging.info(f"Removing {len(ingredients)} ingredient(s) from the pantry for user_id {user_id}")
                
                for ing in ingredients:
                    sql_decrement = """
                    UPDATE Pantry
                    SET quantity = quantity - %s
                    WHERE user_id = %s AND ingredient_id = %s
                    """
                    cursor.execute(sql_decrement, (ing['quantity'], user_id, ing['ingredient_id']))
                    
                    # Optionally delete rows where the quantity becomes zero or less
                    sql_delete = """
                    DELETE FROM Pantry
                    WHERE user_id = %s AND ingredient_id = %s AND quantity <= 0
                    """
                    cursor.execute(sql_delete, (user_id, ing['ingredient_id']))

                self.db.commit()

            logging.info(f"Successfully removed {len(ingredients)} ingredient(s) from the pantry for user_id {user_id}")
            return {"message": f"Successfully removed {len(ingredients)} ingredient(s) from the pantry"}

        except Exception as e:
            self.db.rollback()
            logging.error(f"Error removing ingredients from the pantry for user_id {user_id}: {str(e)}", exc_info=True)
            return {"error": "An error occurred while removing ingredients from the pantry", "details": str(e)}
