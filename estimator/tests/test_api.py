from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_estimate_rejects_short_transcription() -> None:
    response = client.post(
        "/api/v1/estimate",
        json={"transcription": "Texto corto"},
    )

    assert response.status_code == 422