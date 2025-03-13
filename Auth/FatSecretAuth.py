import requests
from Config.SecretManager import get_secret

class FatSecretAuth:
    """FatSecret authentication using AWS Secrets Manager"""

    def __init__(self, region_name="us-east-1"):
        self.secret_name = "Fat-Secret/Credentials"
        self.region_name = region_name
        self.credentials = self.load_credentials()

    def load_credentials(self):
        try:
            return get_secret(self.secret_name, self.region_name)
        except Exception as e:
            print(f"Failed to load FatSecret credentials: {e}")
            return None

    def fetch_access_token(self):
        if not self.credentials:
            print("Error: Missing credentials.")
            return None

        token_url = self.credentials.get("Access-Token-URL")
        grant_type = self.credentials.get("Grant-Type")
        client_id = self.credentials.get("Client-ID")
        client_secret = self.credentials.get("Client-Secret")
        scope = self.credentials.get("Scope")

        if not all([token_url, grant_type, client_id, client_secret, scope]):
            print("Error: Missing credentials.")
            return None

        headers = {
            "Authorization": f"Basic {requests.auth._basic_auth_str(client_id, client_secret)}",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        payload = {
            "grant_type": grant_type,
            "scope": scope
        }

        try:
            response = requests.post(token_url, headers=headers, data=payload)
            response.raise_for_status()
            return response.json().get("access_token")
        except requests.exceptions.RequestException as e:
            print(f"Error fetching FatSecret token: {e}")
            return None
