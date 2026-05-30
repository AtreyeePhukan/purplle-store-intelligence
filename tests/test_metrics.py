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