def test_login_success(client, test_user):
    resp = client.post("/auth/login", json={"login": "alice", "password": "secret123"})
    assert resp.status_code == 200
    body = resp.json()
    assert "access_token" in body
    assert "refresh_token" in body


def test_login_wrong_password(client, test_user):
    resp = client.post("/auth/login", json={"login": "alice", "password": "wrong"})
    assert resp.status_code == 401


def test_login_unknown_user(client):
    resp = client.post("/auth/login", json={"login": "ghost", "password": "whatever"})
    assert resp.status_code == 401


def test_me_requires_token(client):
    resp = client.get("/auth/me")
    assert resp.status_code == 401


def test_me_with_invalid_token(client):
    resp = client.get("/auth/me", headers={"Authorization": "Bearer garbage"})
    assert resp.status_code == 401


def test_me_with_valid_token(client, auth_headers):
    resp = client.get("/auth/me", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["login"] == "alice"


def test_refresh_flow(client, test_user):
    login_resp = client.post("/auth/login", json={"login": "alice", "password": "secret123"})
    refresh_token = login_resp.json()["refresh_token"]

    resp = client.post("/auth/refresh", json={"refresh_token": refresh_token})
    assert resp.status_code == 200
    new_access = resp.json()["access_token"]

    me_resp = client.get("/auth/me", headers={"Authorization": f"Bearer {new_access}"})
    assert me_resp.status_code == 200


def test_refresh_rejects_access_token(client, auth_headers):
    access_token = auth_headers["Authorization"].split(" ")[1]
    resp = client.post("/auth/refresh", json={"refresh_token": access_token})
    assert resp.status_code == 401
