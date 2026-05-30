# PROMPT:
# Generate a pytest test for a FastAPI analytics endpoint that returns
# store metrics. Verify that the endpoint responds successfully and that
# the expected metric fields are present in the JSON response.
# Use FastAPI TestClient and write assertions that are resilient to
# changing metric values.

# CHANGES MADE:
# Updated endpoint paths to match the implemented store metrics API.
# Modified assertions to validate the actual schema returned by the
# application instead of hard-coded values.
# Simplified test logic to ensure compatibility with the SQLite-backed
# analytics implementation.


from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_metrics_endpoint():

    response = client.get(
        "/stores/ST1008/metrics"
    )

    assert response.status_code == 200

    data = response.json()

    assert "store_id" in data
    assert "unique_visitors" in data
    assert "entries" in data
    assert "exits" in data