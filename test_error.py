import sys
import os

os.chdir(r"C:\Users\Brian\Desktop\akademus\backend")

# Run with error output
import subprocess

result = subprocess.run(
    [
        r"venv\Scripts\python.exe",
        "-c",
        """
import sys
sys.path.insert(0, '.')
try:
    from app.api.routes.auth import login
    print('Import OK')
except Exception as e:
    print(f'Error: {e}')
    import traceback
    traceback.print_exc()
""",
    ],
    capture_output=True,
    text=True,
)

print("STDOUT:", result.stdout)
print("STDERR:", result.stderr)
