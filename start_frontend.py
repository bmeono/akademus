import subprocess
import os
import time

os.chdir(r"C:\Users\Brian\Desktop\akademus\frontend")

# Use full path to node_modules
process = subprocess.Popen(
    ["node", "node_modules/vite/bin/vite.js", "--port", "5173"],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
)

time.sleep(5)

if process.poll() is None:
    print("Frontend running on http://localhost:5173")
    print("Open in browser: http://localhost:5173")
else:
    stdout, stderr = process.communicate()
    print(f"Error: {stderr.decode()}")
