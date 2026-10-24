"""
Tests for application bootstrap, health route, error handlers, and audit stub.
"""
from services.audit_service import log as audit_log


def test_health_check(client):
    """Confirm /api/health returns 200 and standard envelope with synthetic notice."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.get_json()
    assert data["ok"] is True
    assert data["data"]["status"] == "healthy"
    assert "synthetic" in data["data"]["notice"].lower()


def test_unknown_url_returns_json_error(client):
    """Confirm 404 handler returns JSON error envelope rather than HTML error."""
    response = client.get("/api/unknown-endpoint-xyz-12345")
    assert response.status_code == 404
    data = response.get_json()
    assert data is not None
    assert data["ok"] is False
    assert data["error"]["code"] == "NOT_FOUND"
    assert "message" in data["error"]


def test_audit_service_log_stub(app):
    """Confirm audit_service.log executes cleanly with agreed signature."""
    with app.app_context():
        record = audit_log(
            actor="test_user",
            action="BOOTSTRAP_TEST",
            entity_type="SYSTEM",
            entity_id="init",
            details={"step": "A0"},
            institution_id=None
        )
        assert record["actor"] == "test_user"
        assert record["action"] == "BOOTSTRAP_TEST"
        assert record["entity_id"] == "init"
