import requests
import base64
import json
from Config.SecretManager import get_secret  

class FatSecretAuth:
    """FatSecret authentication using AWS Secrets Manager"""

    def __init__(self, region_name="us-east-1"):
        self.secret_name = "Fat-Secret/Credentials"
        self.region_name = region_name
        self.credentials = self.load_credentials()

    def load_credentials(self):
        """
        Retrieve FatSecret credentials from AWS Secrets Manager.
        """
        try:
            secret_value = get_secret(self.secret_name, self.region_name)
            
            if isinstance(secret_value, str):
                secret_value = json.loads(secret_value) 

            return secret_value
        except Exception as e:
            print(f"Failed to load FatSecret credentials: {e}")
            return None

    def fetch_access_token(self):
        """
        Fetches FatSecret access token using client credentials.
        """
        if not self.credentials:
            print("Error: Missing credentials from AWS Secrets Manager.")
            return None

        token_url = self.credentials.get("Access-Token-URL", "https://oauth.fatsecret.com/connect/token")
        client_id = self.credentials.get("Client-ID")
        client_secret = self.credentials.get("Client-Secret")
        scope = self.credentials.get("Scope", "premier") 

        if not all([token_url, client_id, client_secret, scope]):
            print("Error: Missing required credentials from AWS.")
            return None

        auth_string = f"{client_id}:{client_secret}"
        auth_header = base64.b64encode(auth_string.encode()).decode()

        headers = {
            "Authorization": f"Basic {auth_header}",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        payload = f"grant_type=client_credentials&scope={scope}"  

        try:
            response = requests.post(token_url, headers=headers, data=payload)
            response.raise_for_status()
            return response.json().get("access_token")
        except requests.exceptions.HTTPError as e:
            print(f"Error fetching FatSecret token: {e}")
            print("Response:", response.text)  
            return None
