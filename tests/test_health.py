import pytest

from app.services import health as health_service


@pytest.fixture
def healthy_dependencies(monkeypatch):
    monkeypatch.setattr(health_service, "check_database", lambda: "ok")
    monkeypatch.setattr(health_service, "check_redis", lambda: "ok")
    monkeypatch.setattr(health_service, "check_workers", lambda: "ok")


def test_root_is_reachable(client):
    response = client.get("/")

    assert response.status_code == 200
    assert "running" in response.json()["msg"]


def test_health_reports_ok_when_all_checks_pass(client, healthy_dependencies):
    response = client.get("/api/v1/health")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["checks"] == {"database": "ok", "redis": "ok", "workers": "ok"}
    assert body["version"]


def test_health_reports_degraded_when_a_check_fails(
    client, healthy_dependencies, monkeypatch
):
    monkeypatch.setattr(
        health_service, "check_database", lambda: "error: OperationalError"
    )

    response = client.get("/api/v1/health")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "degraded"
    assert body["checks"]["database"] == "error: OperationalError"
    assert body["checks"]["redis"] == "ok"


def test_health_reports_missing_workers(client, healthy_dependencies, monkeypatch):
    monkeypatch.setattr(health_service, "check_workers", lambda: "unavailable")

    response = client.get("/api/v1/health")

    assert response.json()["status"] == "degraded"
    assert response.json()["checks"]["workers"] == "unavailable"
