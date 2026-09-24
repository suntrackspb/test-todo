def test_create_and_get_project(client, auth_headers):
    resp = client.post("/projects", json={"title": "Work"}, headers=auth_headers)
    assert resp.status_code == 201
    project_id = resp.json()["id"]

    get_resp = client.get(f"/projects/{project_id}", headers=auth_headers)
    assert get_resp.status_code == 200
    assert get_resp.json()["title"] == "Work"


def test_create_nested_project(client, auth_headers):
    parent = client.post("/projects", json={"title": "Parent"}, headers=auth_headers).json()
    child_resp = client.post(
        "/projects", json={"title": "Child", "parent_id": parent["id"]}, headers=auth_headers
    )
    assert child_resp.status_code == 201
    assert child_resp.json()["parent_id"] == parent["id"]


def test_tree_endpoint_nests_children(client, auth_headers):
    parent = client.post("/projects", json={"title": "Parent"}, headers=auth_headers).json()
    client.post("/projects", json={"title": "Child", "parent_id": parent["id"]}, headers=auth_headers)

    tree_resp = client.get("/projects/tree", headers=auth_headers)
    assert tree_resp.status_code == 200
    tree = tree_resp.json()
    root = next(p for p in tree if p["id"] == parent["id"])
    assert len(root["children"]) == 1
    assert root["children"][0]["title"] == "Child"


def test_update_project_title(client, auth_headers):
    project = client.post("/projects", json={"title": "Old"}, headers=auth_headers).json()
    resp = client.patch(f"/projects/{project['id']}", json={"title": "New"}, headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["title"] == "New"


def test_delete_project_cascades_children(client, auth_headers):
    parent = client.post("/projects", json={"title": "Parent"}, headers=auth_headers).json()
    child = client.post(
        "/projects", json={"title": "Child", "parent_id": parent["id"]}, headers=auth_headers
    ).json()

    del_resp = client.delete(f"/projects/{parent['id']}", headers=auth_headers)
    assert del_resp.status_code == 204

    assert client.get(f"/projects/{child['id']}", headers=auth_headers).status_code == 404


def test_cannot_access_other_users_project(client, auth_headers, other_auth_headers):
    project = client.post("/projects", json={"title": "Secret"}, headers=auth_headers).json()
    resp = client.get(f"/projects/{project['id']}", headers=other_auth_headers)
    assert resp.status_code == 404


def test_project_cannot_be_own_parent(client, auth_headers):
    project = client.post("/projects", json={"title": "Loop"}, headers=auth_headers).json()
    resp = client.patch(
        f"/projects/{project['id']}", json={"parent_id": project["id"]}, headers=auth_headers
    )
    assert resp.status_code == 400
