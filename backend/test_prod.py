import requests

try:
    r = requests.post("https://akademus.onrender.com/auth/login", json={
        "email": "admin@akademus.com",
        "password": "admin123"
    }, timeout=30)
    print(f"Status: {r.status_code}")
    print(r.text[:500])
except Exception as e:
    print(f"Error: {e}")