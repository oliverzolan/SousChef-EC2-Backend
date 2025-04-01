import logging

class CategoryModel:
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

    def get_category_by_subcategory(self, subcategory_name):
        """
        Fetch category ID based on a given subcategory name.
        """
        try:
            with self.db.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT c.name 
                    FROM Subcategories s
                    JOIN Categories c ON s.category_id = c.id
                    WHERE s.name = %s;
                    """,
                    (subcategory_name,)
                )
                category = cursor.fetchone()

            if not category:
                logging.info(f"No category found for subcategory {subcategory_name}.")
                return {"message": f"No category found for subcategory {subcategory_name}."}

            logging.info(f"Fetched category {category['name']} for subcategory {subcategory_name}.")
            return category['name']

        except Exception as e:
            logging.error(f"Error fetching category for subcategory {subcategory_name}: {str(e)}", exc_info=True)
            return {"error": "Error while fetching category", "details": str(e)}
