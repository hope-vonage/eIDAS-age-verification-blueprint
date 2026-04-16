import requests
import json

# The URL of the registration endpoint
url = "http://127.0.0.1:5000/registration"

# The client information
client_info = {
    "redirect_uris": ["https://client.example.com/cb"],
    "client_name": "My Awesome Client",
    "token_endpoint_auth_method": "client_secret_basic",
    "scope": "openid profile email phone",
    "response_types": ["code"],
    "grant_types": ["authorization_code", "refresh_token"],
}

# Send the POST request
response = requests.post(url, json=client_info)

# Print the response
print(response.status_code)
print(response.json())
