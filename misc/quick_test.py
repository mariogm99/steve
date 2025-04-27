import json
from pathlib import Path
from whoopy import WhoopClient

TOKEN_PATH = Path(".tokens/token.json")
CONF       = json.load(open("config.json"))

client = WhoopClient.from_token(
            TOKEN_PATH,
            CONF["client_id"],
            CONF["client_secret"])

user_data = client.user.profile()
print(f"Name: {user_data.first_name} {user_data.last_name}")

