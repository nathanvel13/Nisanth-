from fastapi.testclient import TestClient

from backend.main import app

client = TestClient(app)


def test_root_and_health():
    root = client.get("/")
    assert root.status_code == 200
    assert root.json()["service"] == "backend-api"

    health = client.get("/health")
    assert health.status_code == 200
    assert health.json()["status"] == "ok"


def test_qa_validation_and_demo_response():
    bad = client.post("/qa", json={"text": ""})
    assert bad.status_code == 422

    good = client.post("/qa", json={"text": "Which is the largest ocean?", "level": "beginner"})
    assert good.status_code == 200
    assert good.json()["success"] is True
    assert good.json()["model"] == "demo"


def test_explain_summary_and_learning_routes():
    for path, payload in [
        ("/explain", {"text": "photosynthesis"}),
        ("/summarize", {"text": "Water changes state as temperature changes."}),
        ("/learn/recommendations", {"text": "SQL", "level": "beginner", "weeks": 4}),
    ]:
        response = client.post(path, json=payload)
        assert response.status_code == 200
        assert response.json()["success"] is True


def test_quiz_route():
    response = client.post("/quiz", json={"text": "Pythagorean theorem", "count": 3})
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert len(body["questions"]) == 3
    assert all(len(item["options"]) == 4 for item in body["questions"])
