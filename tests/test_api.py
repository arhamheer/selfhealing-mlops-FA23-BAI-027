import pytest
import requests

BASE_URL = "http://100.50.10.159:32500"


def test_health_endpoint():
    response = requests.get(f"{BASE_URL}/health")
    assert response.status_code == 200
    data = response.json()
    assert data.get("status") == "healthy"
    assert "model_version" in data


def test_predict_returns_label_and_confidence():
    payload = {"text": "This is a great product"}
    response = requests.post(f"{BASE_URL}/predict", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data.get("label") in ["POSITIVE", "NEGATIVE"]
    assert 0 <= data.get("confidence") <= 1
    assert "model_version" in data


def test_predict_negative_text():
    payload = {"text": "This is absolutely terrible and horrible"}
    response = requests.post(f"{BASE_URL}/predict", json=payload)
    assert response.status_code == 200


def test_health_returns_model_version_unstable():
    response = requests.get(f"{BASE_URL}/health")
    assert response.status_code == 200
    data = response.json()
    assert data.get("model_version") == "unstable-v1"
