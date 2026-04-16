import requests

class CamaraClient:
    def __init__(self, api_key, api_secret):
        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = "https://camara.vonage.com" # This is a placeholder

    def verify_age(self, phone_number, age):
        # TODO: replace with real CAMARA API call
        result = True  # Always pass for local testing
        print(f"[DUMMY] Verifying age for {phone_number} is over {age}: {result}")
        return result
