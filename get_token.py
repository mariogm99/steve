import requests
import json
import os

# Whoop API credentials
CLIENT_ID = "42d417ba-39ba-47fe-8f31-cbf4f1072b0d"  # Replace with your actual client ID
CLIENT_SECRET = "82335d3886b8ede314eef61b4a2d981473a2c95744dc01d7dab775b87cd570b0"  # Replace with your actual client secret
REDIRECT_URI = "http://localhost:8000/callback"

TOKEN_URL = "https://api.prod.whoop.com/oauth/oauth2/token"
TOKEN_FILE = "token.json"

def save_tokens(access_token, refresh_token):
    """ Save tokens to a file """
    tokens = {"access_token": access_token, "refresh_token": refresh_token}
    with open(TOKEN_FILE, "w") as f:
        json.dump(tokens, f)

def load_tokens():
    """ Load tokens from file if available """
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, "r") as f:
            return json.load(f)
    return None

def get_new_access_token(auth_code):
    """ Exchange authorization code for new access token """
    data = {
        "grant_type": "authorization_code",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "code": auth_code,
        "redirect_uri": REDIRECT_URI
    }
    response = requests.post(TOKEN_URL, data=data)
    
    print("Response Status Code:", response.status_code)
    print("Response JSON:", response.json())  # Print the full response to debug

    if response.status_code == 200:
        token_info = response.json()
        access_token = token_info.get("access_token")
        refresh_token = token_info.get("refresh_token")  # Get refresh token safely
        
        if not refresh_token:
            print("Warning: No refresh_token received. API might not be issuing one.")
        
        save_tokens(access_token, refresh_token)
        print("New Access Token:", access_token)
    else:
        print("Error:", response.status_code, response.text)


def refresh_access_token(refresh_token):
    """ Use refresh token to get a new access token """
    data = {
        "grant_type": "refresh_token",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "refresh_token": refresh_token
    }
    response = requests.post(TOKEN_URL, data=data)

    if response.status_code == 200:
        token_info = response.json()
        save_tokens(token_info["access_token"], token_info["refresh_token"])
        print("Refreshed Access Token:", token_info["access_token"])
    else:
        print("Error refreshing token:", response.status_code, response.text)

if __name__ == "__main__":
    tokens = load_tokens()

    if tokens:
        print("Using Refresh Token to Get New Access Token...")
        refresh_access_token(tokens["refresh_token"])
    else:
        auth_code = input("Enter the new authorization code: ").strip()
        get_new_access_token(auth_code)
