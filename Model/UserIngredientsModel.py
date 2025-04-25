import logging
from datetime import datetime

class UserIngredientsModel:
    def __init__(self, db_connection):
        self.db = db_connection

    def get_all_user_ingredients(self, user_id):
        """
        Fetch all ingredients for a specific user.
        """
        try:
            with self.db.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT 
                        ui.edamam_food_id,
                        ui.quantity,
                        ui.date_added,
                        ii.Name,
                        ii.Category,
                        ii.Quantity_Type,
                        ii.Expiration_Duration,
                        ii.Image_URL,
                        ii.Fat,
                        ii.Cholesterol,
                        ii.Sodium,
                        ii.Potassium,
                        ii.Carbohydrate,
                        ii.Protein,
                        ii.Calorie,
                        ii.Quantity AS internal_quantity
                    FROM UserIngredients ui
                    JOIN InternalIngredients ii
                        ON ui.edamam_food_id = ii.Edamam_Food_ID
                    WHERE ui.user_id = %s
                    """,
                    (user_id,)
                )
                ingredients = cursor.fetchall()

            if not ingredients:
                logging.info(f"No ingredients found for user_id {user_id}")
                return []

            logging.info(f"Fetched {len(ingredients)} ingredients for user_id {user_id}")
            return ingredients

        except Exception as e:
            logging.error(f"Error fetching ingredients for user_id {user_id}: {str(e)}", exc_info=True)
            return {"error": "An error occurred while fetching ingredients", "details": str(e)}

    def update_user_ingredients_batch(self, user_id, ingredients):
        """
        Insert or update user ingredients.
        If quantity becomes 0, the ingredient is removed instead.
        """
        try:
            if not ingredients or not all('edamam_food_id' in ing and 'quantity' in ing for ing in ingredients):
                logging.warning("[update_user_ingredients_batch] Invalid input")
                return {"error": "Each ingredient must have 'edamam_food_id' and 'quantity'"}

            with self.db.cursor() as cursor:
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                insert_data = []
                delete_data = []

                for ing in ingredients:
                    if int(ing['quantity']) == 0:
                        delete_data.append((user_id, ing['edamam_food_id']))
                    else:
                        insert_data.append((
                            user_id,
                            ing['edamam_food_id'],
                            ing['quantity'],
                            timestamp
                        ))

                if insert_data:
                    cursor.executemany(
                        """
                        INSERT INTO UserIngredients (user_id, edamam_food_id, quantity, date_added)
                        VALUES (%s, %s, %s, %s)
                        ON DUPLICATE KEY UPDATE 
                            quantity = quantity + VALUES(quantity),
                            date_added = VALUES(date_added)
                        """,
                        insert_data
                    )

                if delete_data:
                    cursor.executemany(
                        """
                        DELETE FROM UserIngredients
                        WHERE user_id = %s AND edamam_food_id = %s
                        """,
                        delete_data
                    )

                self.db.commit()

            logging.info(f"Successfully updated ingredients for user_id {user_id}")
            return {"message": f"Updated {len(insert_data)} and removed {len(delete_data)} ingredients"}

        except Exception as e:
            self.db.rollback()
            logging.error(f"Error adding ingredients for user_id {user_id}: {str(e)}", exc_info=True)
            return {"error": "An error occurred while adding ingredients", "details": str(e)}

    def get_all_ingredients_expiring_soon_grouped_by_user(self):
        """
        Gets ingredients that are expiring within 24 hours from all users
        """
        try:
            with self.db.cursor(dictionary=True) as cursor:
                cursor.execute(
                    """
                    SELECT ui.user_id, ui.edamam_food_id, ui.quantity, ui.date_added,
                        ii.Name, ii.Expiration_Duration,
                        TIMESTAMPDIFF(DAY, ui.date_added, NOW()) AS days_elapsed,
                        (ii.Expiration_Duration - TIMESTAMPDIFF(DAY, ui.date_added, NOW())) AS days_left
                    FROM UserIngredients ui
                    JOIN InternalIngredients ii
                        ON ui.edamam_food_id = ii.Edamam_Food_ID
                    WHERE (ii.Expiration_Duration - TIMESTAMPDIFF(DAY, ui.date_added, NOW())) <= 1
                    AND (ii.Expiration_Duration - TIMESTAMPDIFF(DAY, ui.date_added, NOW())) >= 0
                    """
                )
                rows = cursor.fetchall()

            grouped = {}
            for row in rows:
                user_id = row['user_id']
                if user_id not in grouped:
                    grouped[user_id] = []
                grouped[user_id].append(row)

            logging.info(f"Grouped expiring ingredients for {len(grouped)} users")
            return grouped

        except Exception as e:
            logging.error(f"Error fetching all expiring ingredients: {str(e)}", exc_info=True)
            return {"error": "An error occurred while checking for expiring ingredients", "details": str(e)}

    def get_ingredients_expiring_soon_for_user(self, user_id):
        """
        Gets ingredients that are expiring within 24 hours for a specific user.
        """
        try:
            with self.db.cursor(dictionary=True) as cursor:
                cursor.execute(
                    """
                    SELECT ui.user_id, ui.edamam_food_id, ui.quantity, ui.date_added,
                        ii.Name, ii.Expiration_Duration,
                        TIMESTAMPDIFF(DAY, ui.date_added, NOW()) AS days_elapsed,
                        (ii.Expiration_Duration - TIMESTAMPDIFF(DAY, ui.date_added, NOW())) AS days_left
                    FROM UserIngredients ui
                    JOIN InternalIngredients ii
                    ON ui.edamam_food_id = ii.Edamam_Food_ID
                    WHERE (ii.Expiration_Duration - TIMESTAMPDIFF(DAY, ui.date_added, NOW())) BETWEEN 0 AND 1
                    AND ui.user_id = %s
                    """, 
                    (user_id,)
                )
                rows = cursor.fetchall()

            logging.info(f"Fetched {len(rows)} expiring ingredients for user {user_id}")
            return rows

        except Exception as e:
            logging.error(f"Error fetching expiring ingredients for user {user_id}: {str(e)}", exc_info=True)
            return {"error": "An error occurred while checking for expiring ingredients", "details": str(e)}
