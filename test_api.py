import requests
import traceback

try:
    r = requests.post(
        "http://127.0.0.1:8001/auth/login",
        json={"email": "test@akademus.com", "password": "test123"},
    )
    print("Status:", r.status_code)
    print("Response:", r.text)
except Exception as e:
    print("Error:", e)
    traceback.print_exc()
