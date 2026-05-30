# PROMPT:
# Generate a pytest test for a FastAPI health endpoint that verifies
# service availability and checks that a JSON health status is returned.
# Use FastAPI TestClient and avoid external dependencies.

# CHANGES MADE:
# Adapted imports to the project layout.
# Updated assertions to match the implemented /health endpoint response.
# Simplified the test to focus on deployment readiness and service health.

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"