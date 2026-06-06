from fastapi.testclient import TestClient
from api import app

client = TestClient(app)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_predict_valid():
    payload = {
        "store_id": 1,
        "sku_id": 1,
        "date": "2026-06-10",
        "price": 99.9,
        "on_promotion": False,
        "discount_percent": 0,
        "temperature": 20
    }
    response = client.post("/predict", json=payload)
    assert response.status_code == 200
    assert "forecast_qty" in response.json()