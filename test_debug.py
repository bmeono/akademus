import subprocess
import os

os.chdir(r"C:\Users\Brian\Desktop\akademus\backend")

# Run uvicorn and capture output
proc = subprocess.Popen(
    [r"venv\Scripts\python.exe", "-m", "uvicorn", "app.main:app", "--port", "8002"],
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True,
)

# Wait for server to start
import time

time.sleep(3)

# Test login
import requests

try:
    r = requests.post(
        "http://127.0.0.1:8002/auth/login",
        json={"email": "test@akademus.com", "password": "test123"},
    )
    print("Status:", r.status_code)
    print("Response:", r.text)
except Exception as e:
    print("Error:", e)

# Show server output
print("\n--- Server Output ---")
for line in proc.stdout.readlines()[:20]:
    print(line, end="")

proc.terminate()
