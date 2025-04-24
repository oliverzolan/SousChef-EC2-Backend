# import logging
# from Config.Db import Database
# from Api.FatSecret import FatSecretComponent
# from Model.CategoryModel import CategoryModel

# logging.basicConfig(
#     filename='/var/log/fatsecret_sync.log',
#     level=logging.INFO,
#     format='%(asctime)s - %(levelname)s - %(message)s'
# )

# def sync_fatsecret_category():
#     """
#     Syncs FatSecret categories and subcategories.
#     """
#     logging.info("[sync_fatsecret_data] Starting FatSecret sync")

#     try:
#         db_connection = Database().connect_write()
#         category_model = CategoryModel(db_connection)
#         fatsecret = FatSecretComponent()

#         categories = fatsecret.get_food_categories()
#         if not categories:
#             logging.error("[sync_fatsecret_data] Failed to fetch categories.")
#             return

#         for category in categories:
#             category_id = int(category["id"])
#             category_name = category["name"]
#             category_description = "" 

#             category_model.insert_or_update_category(category_id, category_name, category_description)

#             subcategories = fatsecret.get_food_sub_categories(category_id)
#             if subcategories:
#                 for subcategory in subcategories:
#                     category_model.insert_or_update_subcategory(subcategory, category_id)

#         logging.info("[sync_fatsecret_data] Sync successfully.")

#     except Exception as e:
#         logging.error(f"[sync_fatsecret_data] Error during sync: {str(e)}", exc_info=True)

#     finally:
#         if db_connection:
#             db_connection.close()
#             logging.info("[sync_fatsecret_data] Database connection closed.")

# if __name__ == "__main__":
#     sync_fatsecret_category()
