import requests

# Replace with your actual Whoop API endpoint
url = "https://api.prod.whoop.com/"

response = requests.get(url)

print("Status Code:", response.status_code)
print("Response:", response.text)