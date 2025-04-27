from whoopy import WhoopClient

CLIENT_ID     = "42d417ba-39ba-47fe-8f31-cbf4f1072b0d"
CLIENT_SECRET = "82335d3886b8ede314eef61b4a2d981473a2c95744dc01d7dab775b87cd570b0"
REDIRECT_URI  = "http://localhost:8000/callback"

# Step 1 – Get the URL the user should visit
auth_url = WhoopClient.auth_url(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    redirect_uri=REDIRECT_URI,
    scope="offline read:cycles read:sleep read:recovery read:workout"
)
print("Open this URL in a browser:", auth_url)

# Step 2 – Paste the ?code=... you get redirected back with
code = input("Paste the 'code' parameter from the redirected URL: ")

# Step 3 – Exchange code for tokens
client = WhoopClient.authorize(
    code, CLIENT_ID, CLIENT_SECRET, REDIRECT_URI
)

# Step 4 – Make API calls (tokens are handled for you)
cycles = client.get_cycle_collection()
print(cycles[:3])
