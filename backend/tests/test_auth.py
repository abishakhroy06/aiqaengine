import pytest


def test_register_success(client):
    response = client.post("/api/v1/auth/register", json={
        "email": "new@test.com",
        "password": "password123",
        "full_name": "New User"
    })
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "new@test.com"
    assert data["full_name"] == "New User"
    assert "hashed_password" not in data


def test_register_duplicate_email(client, test_user):
    response = client.post("/api/v1/auth/register", json={
        "email": test_user.email,
        "password": "password123"
    })
    assert response.status_code == 409


def test_login_success(client, test_user):
    response = client.post("/api/v1/auth/login", data={
        "username": test_user.email,
        "password": "password123"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


def test_login_invalid_password(client, test_user):
    response = client.post("/api/v1/auth/login", data={
        "username": test_user.email,
        "password": "wrongpassword"
    })
    assert response.status_code == 401


def test_login_unknown_email(client):
    response = client.post("/api/v1/auth/login", data={
        "username": "nobody@test.com",
        "password": "password123"
    })
    assert response.status_code == 401


def test_get_me_unauthorized(client):
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 401


def test_get_me_authorized(client, auth_headers):
    response = client.get("/api/v1/auth/me", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"


def test_refresh_token(client, test_user):
    # Login to get refresh token
    login_resp = client.post("/api/v1/auth/login", data={
        "username": test_user.email,
        "password": "password123"
    })
    refresh_token = login_resp.json()["refresh_token"]

    # Refresh
    response = client.post("/api/v1/auth/refresh", json={"refresh_token": refresh_token})
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data


def test_logout(client, test_user):
    login_resp = client.post("/api/v1/auth/login", data={
        "username": test_user.email,
        "password": "password123"
    })
    refresh_token = login_resp.json()["refresh_token"]

    response = client.post("/api/v1/auth/logout", json={"refresh_token": refresh_token})
    assert response.status_code == 200


def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
