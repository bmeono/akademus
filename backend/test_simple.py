# Simple test - run directly
import sys

sys.path.insert(0, ".\\app")

from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)

# Test / endpoint
r = client.get("/")
print("GET / :", r.status_code, r.json())

# Test /health endpoint
r = client.get("/health")
print("GET /health :", r.status_code, r.json())

# Test login
r = client.post(
    "/auth/login", json={"email": "test@akademus.com", "password": "test123"}
)
print("POST /auth/login :", r.status_code)
print("Response:", r.text)
