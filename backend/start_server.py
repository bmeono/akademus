import subprocess
import os
import time

# Change to backend directory
os.chdir(r"C:\Users\Brian\Desktop\akademus\backend")

# Start uvicorn without blocking
process = subprocess.Popen(
    [r"venv\Scripts\python.exe", "-m", "uvicorn", "app.main:app", "--port", "8001"],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
)

# Wait a few seconds to check if it starts
time.sleep(3)

# Check if process is running
if process.poll() is None:
    print("Backend running on http://127.0.0.1:8001")
else:
    stdout, stderr = process.communicate()
    print(f"Error: {stderr.decode()}")
