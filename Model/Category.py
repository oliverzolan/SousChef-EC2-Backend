import logging

class CategoriesModel:
    def __init__(self, db_connection):
        self.db = db_connection

    def insert_or_update_category(self, category_id, name, description):
        """
        Insert or update category.
        """
        try:
            with self.db.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO Categories (id, name, description)
                    VALUES (%s, %s, %s)
                    ON DUPLICATE KEY UPDATE 
                    name = VALUES(name),
                    description = VALUES(description);
                    """,
                    (category_id, name, description)
                )
            self.db.commit()
            logging.info(f"Category {category_id} - '{name}' inserted/updated successfully.")
            return {"message": f"Category {category_id} processed."}

        except Exception as e:
            logging.error(f"Error inserting/updating category {category_id}: {str(e)}", exc_info=True)
            return {"error": "Error while processing category", "details": str(e)}

    def insert_or_update_subcategory(self, subcategory_name, category_id):
        """
        Insert or update subcategory.
        """
        try:
            with self.db.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO Subcategories (name, category_id)
                    VALUES (%s, %s)
                    ON DUPLICATE KEY UPDATE 
                    category_id = VALUES(category_id);
                    """,
                    (subcategory_name, category_id)
                )
            self.db.commit()
            logging.info(f"Subcategory '{subcategory_name}' in category {category_id} inserted/updated successfully.")
            return {"message": f"Subcategory '{subcategory_name}' processed."}

        except Exception as e:
            logging.error(f"Error inserting/updating subcategory '{subcategory_name}': {str(e)}", exc_info=True)
            return {"error": "Error while processing subcategory", "details": str(e)}

    def get_all_categories(self):
        """
        Fetch all categories.
        """
        try:
            with self.db.cursor() as cursor:
                cursor.execute("SELECT id, name, description FROM Categories;")
                categories = cursor.fetchall()

            if not categories:
                logging.info("No categories found.")
                return {"message": "No categories found."}

            logging.info(f"Fetched {len(categories)} categories.")
            return categories

        except Exception as e:
            logging.error(f"Error fetching categories: {str(e)}", exc_info=True)
            return {"error": "Error while fetching categories", "details": str(e)}

    def get_subcategories_by_category(self, category_id):
        """
        Fetch all subcategories.
        """
        try:
            with self.db.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT name 
                    FROM Subcategories 
                    WHERE category_id = %s;
                    """,
                    (category_id,)
                )
                subcategories = cursor.fetchall()

            if not subcategories:
                logging.info(f"No subcategories found for category {category_id}.")
                return {"message": f"No subcategories found for category {category_id}."}

            logging.info(f"Fetched {len(subcategories)} subcategories for category {category_id}.")
            return [sub[0] for sub in subcategories]

        except Exception as e:
            logging.error(f"Error fetching subcategories for category {category_id}: {str(e)}", exc_info=True)
            return {"error": "Error while fetching subcategories", "details": str(e)}
