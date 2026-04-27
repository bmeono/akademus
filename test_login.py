import requests
import json

data = {"email": "test@akademus.com", "password": "test123"}
response = requests.post("http://127.0.0.1:8001/auth/login", json=data)
print("Status:", response.status_code)
print("Response:", response.text)
