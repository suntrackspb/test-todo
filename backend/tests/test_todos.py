def _create_project(client, headers, title="Project"):
    return client.post("/projects", json={"title": title}, headers=headers).json()


def test_create_and_list_todos(client, auth_headers):
    project = _create_project(client, auth_headers)
    resp = client.post(
        f"/projects/{project['id']}/todos",
        json={"title": "Buy milk", "due_date": "2026-10-05"},
        headers=auth_headers,
    )
    assert resp.status_code == 201
    assert resp.json()["status"] == "todo"
    assert resp.json()["priority"] == "none"

    list_resp = client.get(f"/projects/{project['id']}/todos", headers=auth_headers)
    assert len(list_resp.json()) == 1


def test_create_todo_with_priority(client, auth_headers):
    project = _create_project(client, auth_headers)
    resp = client.post(
        f"/projects/{project['id']}/todos",
        json={"title": "Fix prod", "priority": "critical"},
        headers=auth_headers,
    )
    assert resp.status_code == 201
    assert resp.json()["priority"] == "critical"


def test_update_todo_priority(client, auth_headers):
    project = _create_project(client, auth_headers)
    todo = client.post(f"/projects/{project['id']}/todos", json={"title": "Task"}, headers=auth_headers).json()

    resp = client.patch(f"/todos/{todo['id']}", json={"priority": "urgent"}, headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["priority"] == "urgent"


def test_update_todo_status(client, auth_headers):
    project = _create_project(client, auth_headers)
    todo = client.post(f"/projects/{project['id']}/todos", json={"title": "Task"}, headers=auth_headers).json()

    resp = client.patch(f"/todos/{todo['id']}", json={"status": "done"}, headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["status"] == "done"


def test_filter_todos_by_status(client, auth_headers):
    project = _create_project(client, auth_headers)
    t1 = client.post(f"/projects/{project['id']}/todos", json={"title": "A"}, headers=auth_headers).json()
    client.post(f"/projects/{project['id']}/todos", json={"title": "B"}, headers=auth_headers)
    client.patch(f"/todos/{t1['id']}", json={"status": "done"}, headers=auth_headers)

    resp = client.get(f"/projects/{project['id']}/todos?status=done", headers=auth_headers)
    assert resp.status_code == 200
    titles = [t["title"] for t in resp.json()]
    assert titles == ["A"]


def test_delete_todo(client, auth_headers):
    project = _create_project(client, auth_headers)
    todo = client.post(f"/projects/{project['id']}/todos", json={"title": "Task"}, headers=auth_headers).json()

    del_resp = client.delete(f"/todos/{todo['id']}", headers=auth_headers)
    assert del_resp.status_code == 204


def test_cannot_update_other_users_todo(client, auth_headers, other_auth_headers):
    project = _create_project(client, auth_headers)
    todo = client.post(f"/projects/{project['id']}/todos", json={"title": "Task"}, headers=auth_headers).json()

    resp = client.patch(f"/todos/{todo['id']}", json={"status": "done"}, headers=other_auth_headers)
    assert resp.status_code == 404
