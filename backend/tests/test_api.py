import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.config import settings

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_message_too_long():
    long_message = "A" * (settings.max_message_length + 1)
    response = client.post("/chat", json={
        "session_id": "test_session",
        "message": long_message
    })
    assert response.status_code == 400
    assert "too long" in response.json()["detail"]

def test_reset_session():
    response = client.post("/reset", json={"session_id": "test_session"})
    assert response.status_code == 200
    assert response.json()["status"] == "success"
