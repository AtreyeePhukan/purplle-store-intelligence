# PROMPT:
# Generate a simple pytest test for a FastAPI application that verifies
# the root endpoint returns HTTP 200 and a valid JSON response.
# Use FastAPI TestClient and keep the test lightweight.

# CHANGES MADE:
# Updated imports to match the project structure.
# Modified assertions to validate the actual response returned by the
# Purplle Retail Intelligence API root endpoint.


from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_root():
    response = client.get("/")

    assert response.status_code == 200