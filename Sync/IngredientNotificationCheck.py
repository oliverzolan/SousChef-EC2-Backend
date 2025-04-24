import os
import json
import logging
from Config.Db import Database
from Model.UserIngredientsModel import UserIngredientsModel
from apns2.client import APNsClient
from apns2.payload import Payload
from apns2.credentials import TokenCredentials
import os
from dotenv import load_dotenv

load_dotenv()  

# Setup logging
logging.basicConfig(
    filename='/var/log/expiration_notifier.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class ExpiringIngredientNotifierService:
    def __init__(self):
        self.db = Database().connect_read()

        self.credentials = TokenCredentials(
            auth_key_path=os.getenv("APP_AUTH_KEY"),
            team_id=os.getenv("APP_TEAM_ID"),      
            key_id=os.getenv("APP_KEY_ID")               
        )
        self.apns_client = APNsClient(
            credentials=self.credentials,
            use_sandbox=True,                 
            team_id=os.getenv("APP_TEAM_ID"),
            key_id=os.getenv("APP_KEY_ID")  
        )
        self.apns_topic = 'com.your.bundle.id'  

    def get_users_with_expiring_ingredients(self):
        """
        Collects a dictionary of user_id -> list of expiring ingredients (within 24h).
        """
        try:
            model = UserIngredientsModel(self.db)
            grouped_results = model.get_all_ingredients_expiring_soon_grouped_by_user()

            for user_id, items in grouped_results.items():
                logging.info(f"[Notifier] User {user_id} has {len(items)} expiring ingredients")

            return grouped_results

        except Exception as e:
            logging.error(f"[Notifier] Error while fetching expiring ingredients: {str(e)}", exc_info=True)
            return {}

        finally:
            if self.db:
                self.db.close()
                logging.info("[Notifier] Database connection closed")

    def send_notification(self, device_token, message):
        """
        Sends a push notification to the given device token.
        """
        try:
            payload = Payload(alert=message, sound="default", badge=1)
            self.apns_client.send_notification(device_token, payload, topic=self.apns_topic)
            logging.info(f"[Notifier] Sent notification to {device_token}")
        except Exception as e:
            logging.error(f"[Notifier] Failed to send notification: {str(e)}", exc_info=True)

    def get_device_token(self, user_id):
        """
        Fetch the device token from the database.
        You must implement this based on your schema.
        """
        try:
            cursor = self.db.cursor()
            cursor.execute("SELECT device_token FROM users WHERE id = %s", (user_id,))
            result = cursor.fetchone()
            return result[0] if result else None
        except Exception as e:
            logging.error(f"[Notifier] Error fetching device token for user {user_id}: {str(e)}", exc_info=True)
            return None

    def notify_users(self, grouped_results):
        for user_id, items in grouped_results.items():
            device_token = self.get_device_token(user_id)
            if not device_token:
                logging.warning(f"[Notifier] No device token for user {user_id}")
                continue

            message = f"You have {len(items)} ingredient(s) expiring soon."
            self.send_notification(device_token, message)


if __name__ == "__main__":
    service = ExpiringIngredientNotifierService()
    expiring_data = service.get_users_with_expiring_ingredients()

    if expiring_data:
        service.notify_users(expiring_data)

    print(json.dumps(expiring_data, indent=2))
