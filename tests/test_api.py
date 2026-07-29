from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_creates_png() -> None:
    response = client.post("/v1/images", json={"prompt": "a blue sky", "width": 128, "height": 128})
    assert response.status_code == 200
    assert response.headers["content-type"] == "image/png"
    assert response.content.startswith(b"\x89PNG\r\n\x1a\n")


def test_rejects_empty_prompt() -> None:
    assert client.post("/v1/images", json={"prompt": ""}).status_code == 422
