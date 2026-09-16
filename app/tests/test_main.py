from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_home():
    response = client.get("/")

    assert response.status_code == 200
    assert "EKS CI/CD Demo Application" in response.text
    assert "v1.0.0" in response.text


def test_health():
    response = client.get("/health")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "healthy"
    assert data["version"] == "v1.0.0"
    assert data["environment"] == "local"


def test_version():
    response = client.get("/version")

    assert response.status_code == 200

    data = response.json()

    assert data["application"] == "EKS CI/CD Demo Application"
    assert data["version"] == "v1.0.0"
    assert data["environment"] == "local"