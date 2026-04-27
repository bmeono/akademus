import sys

sys.path.insert(0, "C:/Users/Brian/Desktop/akademus/backend")

try:
    from app.main import app

    print("Backend OK - FastAPI importa correctamente")
except Exception as e:
    print(f"Error: {e}")
    import traceback

    traceback.print_exc()
