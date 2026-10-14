async def _make_post(client, headers):
    response = await client.post(
        "/api/posts",
        json={"title": "A post", "content": "Some content"},
        headers=headers,
    )
    assert response.status_code == 201
    return response.json()["id"]


async def test_comment_create_and_list(client, auth_headers, other_headers):
    post_id = await _make_post(client, auth_headers)

    response = await client.post(
        f"/api/posts/{post_id}/comments",
        json={"content": "Nice post"},
        headers=other_headers,
    )
    assert response.status_code == 201
    assert response.json()["author"]["username"] == "otheruser"

    response = await client.get(f"/api/posts/{post_id}/comments")
    assert response.status_code == 200
    assert [c["content"] for c in response.json()] == ["Nice post"]


async def test_comment_requires_auth(client, auth_headers):
    post_id = await _make_post(client, auth_headers)
    response = await client.post(f"/api/posts/{post_id}/comments", json={"content": "Hi"})
    assert response.status_code == 401


async def test_empty_comment_rejected(client, auth_headers):
    post_id = await _make_post(client, auth_headers)
    response = await client.post(
        f"/api/posts/{post_id}/comments",
        json={"content": "   "},
        headers=auth_headers,
    )
    assert response.status_code == 422


async def test_comment_on_missing_post(client, auth_headers):
    response = await client.post(
        "/api/posts/9999/comments",
        json={"content": "Hi"},
        headers=auth_headers,
    )
    assert response.status_code == 404


async def test_post_owner_can_delete_any_comment(client, auth_headers, other_headers):
    post_id = await _make_post(client, auth_headers)  
    created = await client.post(
        f"/api/posts/{post_id}/comments",
        json={"content": "From someone else"},
        headers=other_headers,
    )
    comment_id = created.json()["id"]

    response = await client.delete(
        f"/api/posts/{post_id}/comments/{comment_id}",
        headers=auth_headers,
    )
    assert response.status_code == 204


async def test_stranger_cannot_delete_comment(client, auth_headers, other_headers):
    post_id = await _make_post(client, auth_headers) 
    created = await client.post(
        f"/api/posts/{post_id}/comments",
        json={"content": "My own comment"},
        headers=auth_headers,
    )
    comment_id = created.json()["id"]

    # otheruser 
    response = await client.delete(
        f"/api/posts/{post_id}/comments/{comment_id}",
        headers=other_headers,
    )
    assert response.status_code == 403