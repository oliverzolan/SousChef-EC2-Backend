import requests
from Cache.FatSecretCache import get_cached_fatsecret_token

class FatSecretComponent:
    """Handles FatSecret API interactions, including authentication and food recognition."""

    BASE_URL = "https://platform.fatsecret.com/rest"

    def __init__(self):
        self.token = get_cached_fatsecret_token()  

    def make_request(self, endpoint, method="GET", params=None):
        if not self.token:
            self.token = get_cached_fatsecret_token()  

        url = f"{self.BASE_URL}{endpoint}"
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }

        try:
            response = requests.get(url, headers=headers, params=params) if method.upper() == "GET" else None
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            if response.status_code == 401:
                print("Access token expired. Fetching new token")
                self.token = get_cached_fatsecret_token()  
                return self.make_request(endpoint, method, params)
            else:
                print(f"FatSecret API Error: {e}")
                return None

    def search_foods(self, search_expression):
        params = {
            "search_expression": search_expression,
            "include_sub_categories": "true",
            "include_food_images": "false",
            "max_results": "1",
            "format": "json"
        }
        
        response = self.make_request("/foods/search/v3", method="GET", params=params)
        if not response:
            return None

        try:
            food_results = response.get("foods_search", {}).get("results", {}).get("food", [])
            if not food_results:
                return None

            subcategories = food_results[0].get("food_sub_categories", {}).get("food_sub_category", [])
            return subcategories if subcategories else None
        except Exception as e:
            print(f"Error processing response: {e}")
            return None

    def get_food_categories(self):
        params = {"format": "json"}  

        response = self.make_request("/food-categories/v2", method="GET", params=params)
        if not response:
            return None

        try:
            categories = response.get("food_categories", {}).get("food_category", [])
            return [{"id": cat["food_category_id"], "name": cat["food_category_name"]} for cat in categories]
        except Exception as e:
            print(f"Error processing response: {e}")
            return None

    def get_food_sub_categories(self, food_category_id):
        params = {
            "format": "json", 
            "food_category_id": food_category_id
        }

        response = self.make_request("/food-sub-categories/v2", method="GET", params=params)
        if not response:
            return None

        try:
            return response.get("food_sub_categories", {}).get("food_sub_category", [])
        except Exception as e:
            print(f"Error processing response: {e}")
            return None
