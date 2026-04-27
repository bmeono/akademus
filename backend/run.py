import subprocess
import os

os.chdir(r"C:\Users\Brian\Desktop\akademus\backend")
subprocess.run(
    [
        r".\venv\Scripts\python.exe",
        "-m",
        "uvicorn",
        "app.main:app",
        "--host",
        "127.0.0.1",
        "--port",
        "8001",
    ]
)
