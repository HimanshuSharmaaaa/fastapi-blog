async def test_register_and_get_me(client, auth_headers):
    response = await client.get("/api/users/me", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["email"] == "test@example.com"
    assert "password" not in response.json()


async def test_login_wrong_password(client, auth_headers):
    response = await client.post(
        "/api/users/token",
        data={"username": "test@example.com", "password": "wrong-password"},
    )
    assert response.status_code == 401


async def test_me_requires_auth(client):
    response = await client.get("/api/users/me")
    assert response.status_code == 401


async def test_create_post(client, auth_headers):
    response = await client.post(
        "/api/posts",
        json={"title": "Hello", "content": "First post"},
        headers=auth_headers,
    )
    assert response.status_code == 201
    assert response.json()["title"] == "Hello"


async def test_create_post_requires_auth(client):
    response = await client.post("/api/posts", json={"title": "Hello", "content": "x"})
    assert response.status_code == 401