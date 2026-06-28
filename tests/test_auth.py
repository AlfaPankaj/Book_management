from app.schemas.user import UserCreate

def test_register_user(client):
    user_data = {
        "email": "test@example.com",
        "password": "password123",
        "full_name": "Test User"
    }
    response = client.post("/api/v1/auth/register", json=user_data)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["refresh_token"] is not None

def test_login_user(client):
    # First register a user
    user_data = {
        "email": "test2@example.com",
        "password": "password123",
        "full_name": "Test User 2"
    }
    client.post("/api/v1/auth/register", json=user_data)

    # Then login
    login_data = {
        "username": "test2@example.com",
        "password": "password123"
    }
    response = client.post("/api/v1/auth/login", data=login_data)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"