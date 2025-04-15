import requests

token = "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"
headers = {"Authorization": f"token {token}"}

response = requests.get("https://api.github.com/user", headers=headers)

print(response.json())