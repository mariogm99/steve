from whoopy import WhoopClient
from pathlib import Path
import pandas as pd                 # optional

TOKEN_PATH = Path(".tokens/token.json")
CONF       = json.load(open("config.json"))

client = WhoopClient.from_token(TOKEN_PATH,
                                CONF["client_id"],
                                CONF["client_secret"])

# The client auto-refreshes the token when needed

