import firebase_admin
from firebase_admin import credentials, auth
from Config.SecretManager import get_secret
import os
from dotenv import load_dotenv

load_dotenv()
FIREBASE_SECRET = os.getenv("FIREBASE_SECRET")
REGION_NAME = os.getenv("AWS_REGION")


def initialize_firebase():
    """
    Initialize Firebase Admin SDK using credentials from Secrets Manager.
    """
    try:
        firebase_credentials = get_secret(FIREBASE_SECRET, REGION_NAME)
        private_key = firebase_credentials['Private-Key'].replace('\\n', '\n')
        cred = credentials.Certificate({
            "type": "service_account",
            "project_id": firebase_credentials['Project-Id'],
            "private_key_id": firebase_credentials['Project-Key-Id'],
            "private_key": private_key,
            "client_email": firebase_credentials['Client-Email'],
            "client_id": firebase_credentials['Client-Id'],
            "auth_uri": firebase_credentials['Auth-URL'],
            "token_uri": firebase_credentials['Token-Uri'],
            "auth_provider_x509_cert_url": firebase_credentials['Auth-Provider'],
            "client_x509_cert_url": firebase_credentials['Client-Cert']
        })

        if not firebase_admin._apps:
            firebase_admin.initialize_app(cred)
            print("Firebase Admin SDK initialized successfully.")
    except Exception as e:
        print(f"Error initializing Firebase: {e}")
        raise e


def verify_firebase_token(id_token):
    """
    Verify the Firebase ID token and return the decoded token.
    """
    try:
        decoded_token = auth.verify_id_token(id_token)
        return decoded_token
    except Exception as e:
        print(f"Error verifying Firebase token: {e}")
        return None
