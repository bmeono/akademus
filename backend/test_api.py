import requests
import time
time.sleep(2)

r = requests.post("http://localhost:8001/auth/login", json={
    "email": "admin@akademus.com",
    "password": "admin123"
})
print(f"Status: {r.status_code}")
if r.status_code == 200:
    print("Login OK!")
else:
    print(f"Error: {r.text}")