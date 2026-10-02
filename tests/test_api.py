import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)


def test_health():
    res = client.get("/health")
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert data["data"]["status"] == "healthy"


def test_demo_load():
    res = client.post("/demo/load")
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert "metadata" in data["data"]


def test_predict():
    res = client.post("/predict", json={"text": "Experienced Python Software Engineer with FastAPI."})
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert "prediction" in data["data"]


def test_analyze():
    res = client.post("/analyze-resume", data={"text": "John Doe john@example.com +1-555-1234 Bachelor in Computer Science Python SQL"})
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert data["data"]["candidate"]["email"] == "john@example.com"
    assert data["data"]["quality_analysis"]["overall_score"] > 0


def test_match():
    res = client.post("/match", json={
        "resume_text": "Python ML Engineer with Scikit-learn",
        "job_description": "Data Scientist needing Python and ML"
    })
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert "similarity_percentage" in data["data"]
