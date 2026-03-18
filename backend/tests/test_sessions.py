import pytest
from unittest.mock import patch


def test_list_sessions_empty(client, auth_headers):
    response = client.get("/api/v1/sessions", headers=auth_headers)
    assert response.status_code == 200
    assert response.json() == []


def test_list_sessions_with_data(client, auth_headers, test_session):
    response = client.get("/api/v1/sessions", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "Test QA Session"
    assert data[0]["status"] == "complete"


def test_create_session(client, auth_headers):
    with patch("app.routers.sessions.run_generation"):
        response = client.post("/api/v1/sessions", headers=auth_headers, json={
            "name": "New QA Session",
            "requirement": "User can reset their password via email",
            "context": {
                "product": "SaaS App",
                "platform": "Web",
                "users_roles": "Admin, User",
                "rules_constraints": "",
                "risks": "",
                "environment": "Production"
            },
            "template": "full"
        })
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "New QA Session"
    assert data["status"] == "pending"


def test_get_session(client, auth_headers, test_session, test_output):
    response = client.get(f"/api/v1/sessions/{test_session.id}", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == test_session.id
    assert data["output"] is not None
    assert len(data["output"]["test_cases"]["positive"]) == 1


def test_get_session_not_found(client, auth_headers):
    response = client.get("/api/v1/sessions/99999", headers=auth_headers)
    assert response.status_code == 404


def test_get_session_unauthorized(client, test_session):
    response = client.get(f"/api/v1/sessions/{test_session.id}")
    assert response.status_code == 401


def test_delete_session(client, auth_headers, test_session):
    response = client.delete(f"/api/v1/sessions/{test_session.id}", headers=auth_headers)
    assert response.status_code == 204

    # Verify deleted
    get_resp = client.get(f"/api/v1/sessions/{test_session.id}", headers=auth_headers)
    assert get_resp.status_code == 404


def test_export_csv(client, auth_headers, test_session, test_output):
    response = client.get(f"/api/v1/sessions/{test_session.id}/export", headers=auth_headers)
    assert response.status_code == 200
    assert "text/csv" in response.headers["content-type"]
    content = response.text
    assert "TC-POS-001" in content
    assert "Successful login" in content


def test_list_sessions_requires_auth(client):
    response = client.get("/api/v1/sessions")
    assert response.status_code == 401
