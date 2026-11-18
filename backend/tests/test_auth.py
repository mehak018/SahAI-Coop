def test_register_user_success(client):
    response = client.post(
        "/api/auth/register",
        json={
            "name": "Devidas Patil",
            "email": "devidas.patil@example.com",
            "password": "SecurePassword123",
            "preferred_language": "mr"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["email"] == "devidas.patil@example.com"
    assert data["user"]["name"] == "Devidas Patil"
    assert data["user"]["preferred_language"] == "mr"


def test_register_duplicate_email(client):
    payload = {
        "name": "First User",
        "email": "duplicate@example.com",
        "password": "Password123",
        "preferred_language": "en"
    }
    r1 = client.post("/api/auth/register", json=payload)
    assert r1.status_code == 201

    r2 = client.post("/api/auth/register", json=payload)
    assert r2.status_code == 400
    assert "already exists" in r2.json()["detail"]


def test_register_invalid_short_password(client):
    response = client.post(
        "/api/auth/register",
        json={
            "name": "Short Pwd",
            "email": "short@example.com",
            "password": "123",
            "preferred_language": "en"
        }
    )
    assert response.status_code == 422


def test_login_success(client):
    # Register user first
    client.post(
        "/api/auth/register",
        json={
            "name": "Login Test User",
            "email": "login.test@example.com",
            "password": "CorrectPassword123",
            "preferred_language": "hi"
        }
    )

    # Login
    response = client.post(
        "/api/auth/login",
        json={
            "email": "login.test@example.com",
            "password": "CorrectPassword123"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["user"]["email"] == "login.test@example.com"


def test_login_invalid_password(client):
    client.post(
        "/api/auth/register",
        json={
            "name": "Login Fail User",
            "email": "fail@example.com",
            "password": "CorrectPassword123"
        }
    )

    response = client.post(
        "/api/auth/login",
        json={
            "email": "fail@example.com",
            "password": "WrongPassword999"
        }
    )
    assert response.status_code == 401
    assert "Invalid email or password" in response.json()["detail"]


def test_get_current_user_profile(client):
    reg = client.post(
        "/api/auth/register",
        json={
            "name": "Profile User",
            "email": "profile@example.com",
            "password": "Password123",
            "preferred_language": "en"
        }
    )
    token = reg.json()["access_token"]

    response = client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json()["email"] == "profile@example.com"
