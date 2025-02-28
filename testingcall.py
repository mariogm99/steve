import requests
import json
import os

# WHOOP API credentials
CLIENT_ID = "42d417ba-39ba-47fe-8f31-cbf4f1072b0d"  # Replace with your actual client ID
CLIENT_SECRET = "82335d3886b8ede314eef61b4a2d981473a2c95744dc01d7dab775b87cd570b0"  # Replace with your actual client secret
TOKEN_URL = "https://api.prod.whoop.com/oauth/oauth2/token"
TOKEN_FILE = "token.json"

# WHOOP API Endpoints
PROFILE_URL = "https://api.prod.whoop.com/developer/v1/user/profile/basic"
CYCLE_URL = "https://api.prod.whoop.com/developer/v1/cycle?limit=1"
RECOVERY_URL = "https://api.prod.whoop.com/developer/v1/recovery?limit=1"
SLEEP_URL = "https://api.prod.whoop.com/developer/v1/activity/sleep?limit=1"

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
        save_tokens(token_info["access_token"], token_info.get("refresh_token", refresh_token))
        return token_info["access_token"]
    else:
        print("❌ ERROR: Could not refresh token. Response:", response.text)
        return None

def get_access_token():
    """ Get a valid access token, refreshing if necessary """
    tokens = load_tokens()
    if tokens:
        return tokens["access_token"]
    else:
        print("❌ ERROR: No valid access token. Please authenticate again.")
        return None

def get_json_response(url, headers):
    """ Makes a GET request and returns JSON, handling errors. """
    response = requests.get(url, headers=headers)
    
    if response.status_code == 401:
        print("🔄 Token expired. Refreshing...")
        tokens = load_tokens()
        new_access_token = refresh_access_token(tokens["refresh_token"])
        
        if new_access_token:
            headers["Authorization"] = f"Bearer {new_access_token}"
            response = requests.get(url, headers=headers)
        else:
            return None

    if response.status_code != 200:
        print(f"❌ ERROR: Failed to fetch {url}. Status Code: {response.status_code}")
        print("Response:", response.text)
        return None

    return response.json()

# Get latest access token
access_token = get_access_token()
if not access_token:
    exit()

headers = {"Authorization": f"Bearer {access_token}"}

# Get user profile
profile_resp = get_json_response(PROFILE_URL, headers)
username = profile_resp.get("first_name", "User") if profile_resp else "Unknown"

# Get the latest cycle (strain data)
cycle_resp = get_json_response(CYCLE_URL, headers)
latest_cycle = cycle_resp.get("records", [{}])[0] if cycle_resp else {}
strain = latest_cycle.get("score", {}).get("strain", "No strain data available")

# Get the latest recovery data
recovery_resp = get_json_response(RECOVERY_URL, headers)
latest_recovery = recovery_resp.get("records", [{}])[0] if recovery_resp else {}
recovery_score = latest_recovery.get("score", {}).get("recovery_score", "No recovery data available")

# Get the latest sleep data
sleep_resp = get_json_response(SLEEP_URL, headers)
latest_sleep = sleep_resp.get("records", [{}])[0] if sleep_resp else {}
sleep_score = latest_sleep.get("score", {}).get("sleep_performance_percentage", "No sleep data available")

# Determine status based on recovery score
if isinstance(recovery_score, (int, float)):
    if recovery_score >= 67:
        status = "GREEN"
    elif recovery_score >= 34:
        status = "YELLOW"
    else:
        status = "RED"
else:
    status = "UNKNOWN"

# Print formatted output
print(f"""
Hello {username},

Today you are in {status}

Your Sleep is {sleep_score}%
Your Recovery is {recovery_score}%
Your Strain right now is {strain}
""")
