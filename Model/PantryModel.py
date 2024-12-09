class PantryModel:
    def __init__(self, db_connection):
        self.db = db_connection

    def get_pantry_items_by_user_id(self, user_id):
        """
        Fetch all pantry items for a given user ID.
        """
        try:
            with self.db.cursor() as cursor:
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
                return {"message": "User has no items in their pantry"}

            return pantry_items

        except Exception as e:
            # Log the error for debugging purposes
            logging.error(f"Error fetching pantry items for user_id {user_id}: {str(e)}", exc_info=True)
            # Return an error message to the caller
            return {"error": "An error occurred while fetching pantry items", "details": str(e)}
