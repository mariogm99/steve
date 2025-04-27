import json, webbrowser
from pathlib import Path
from whoopy import WhoopClient

CONF = json.load(open("config.json"))
TOKEN_PATH = Path(".tokens/token.json")          # wherever you like

# --- Step 1: build the URL the user must visit -------------------------------
auth_info = WhoopClient.auth_url(CONF["client_id"],
                                CONF["client_secret"],
                                CONF["redirect_uri"])
auth_url = auth_info[0]  # Extract the URL from the tuple

print("Opening browser for WHOOP sign-in …")
webbrowser.open(auth_url)

# --- Step 2: paste the ?code=… parameter you get redirected back with --------
code = input("Paste the code from the redirect URL: ").strip()

# --- Step 3: exchange the code for access + refresh tokens -------------------
client = WhoopClient.authorize(code,
                              CONF["client_id"],
                              CONF["client_secret"],
                              CONF["redirect_uri"])

client.store_token(TOKEN_PATH)           # so you never do the dance again
print("✅ Token stored at", TOKEN_PATH)
