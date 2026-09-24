def _create_project(client, headers):
    return client.post("/projects", json={"title": "P"}, headers=headers).json()


def test_calendar_aggregates_todos_and_notes_in_range(client, auth_headers):
    project = _create_project(client, auth_headers)
    client.post(
        f"/projects/{project['id']}/todos",
        json={"title": "Todo in range", "due_date": "2026-10-05"},
        headers=auth_headers,
    )
    client.post(
        f"/projects/{project['id']}/notes",
        json={"title": "Note in range", "due_date": "2026-10-10"},
        headers=auth_headers,
    )

    resp = client.get("/calendar", params={"from": "2026-10-01", "to": "2026-10-31"}, headers=auth_headers)
    assert resp.status_code == 200
    body = resp.json()
    assert len(body["todos"]) == 1
    assert len(body["notes"]) == 1


def test_calendar_excludes_items_without_due_date(client, auth_headers):
    project = _create_project(client, auth_headers)
    client.post(f"/projects/{project['id']}/todos", json={"title": "No date"}, headers=auth_headers)
    client.post(f"/projects/{project['id']}/notes", json={"title": "No date"}, headers=auth_headers)

    resp = client.get("/calendar", params={"from": "2026-10-01", "to": "2026-10-31"}, headers=auth_headers)
    body = resp.json()
    assert body["todos"] == []
    assert body["notes"] == []


def test_calendar_excludes_items_outside_range(client, auth_headers):
    project = _create_project(client, auth_headers)
    client.post(
        f"/projects/{project['id']}/todos",
        json={"title": "Outside", "due_date": "2026-11-01"},
        headers=auth_headers,
    )

    resp = client.get("/calendar", params={"from": "2026-10-01", "to": "2026-10-31"}, headers=auth_headers)
    assert resp.json()["todos"] == []


def test_calendar_rejects_inverted_range(client, auth_headers):
    resp = client.get("/calendar", params={"from": "2026-10-31", "to": "2026-10-01"}, headers=auth_headers)
    assert resp.status_code == 400


def test_calendar_excludes_done_todos(client, auth_headers):
    project = _create_project(client, auth_headers)
    todo = client.post(
        f"/projects/{project['id']}/todos",
        json={"title": "Finished", "due_date": "2026-10-05"},
        headers=auth_headers,
    ).json()
    client.patch(f"/todos/{todo['id']}", json={"status": "done"}, headers=auth_headers)

    resp = client.get("/calendar", params={"from": "2026-10-01", "to": "2026-10-31"}, headers=auth_headers)
    assert resp.json()["todos"] == []


def test_calendar_todo_includes_priority(client, auth_headers):
    project = _create_project(client, auth_headers)
    client.post(
        f"/projects/{project['id']}/todos",
        json={"title": "Critical", "priority": "critical", "due_date": "2026-10-05"},
        headers=auth_headers,
    )

    resp = client.get("/calendar", params={"from": "2026-10-01", "to": "2026-10-31"}, headers=auth_headers)
    assert resp.json()["todos"][0]["priority"] == "critical"


def test_calendar_filters_by_project_id(client, auth_headers):
    project_a = _create_project(client, auth_headers)
    project_b = _create_project(client, auth_headers)
    client.post(
        f"/projects/{project_a['id']}/todos",
        json={"title": "In A", "due_date": "2026-10-05"},
        headers=auth_headers,
    )
    client.post(
        f"/projects/{project_b['id']}/todos",
        json={"title": "In B", "due_date": "2026-10-06"},
        headers=auth_headers,
    )

    resp = client.get(
        "/calendar",
        params={"from": "2026-10-01", "to": "2026-10-31", "project_id": project_a["id"]},
        headers=auth_headers,
    )
    assert resp.status_code == 200
    todos = resp.json()["todos"]
    assert len(todos) == 1
    assert todos[0]["title"] == "In A"


def test_calendar_rejects_project_id_not_owned(client, auth_headers, other_auth_headers):
    project = _create_project(client, other_auth_headers)

    resp = client.get(
        "/calendar",
        params={"from": "2026-10-01", "to": "2026-10-31", "project_id": project["id"]},
        headers=auth_headers,
    )
    assert resp.status_code == 404


def test_calendar_only_shows_own_projects(client, auth_headers, other_auth_headers):
    project = _create_project(client, other_auth_headers)
    client.post(
        f"/projects/{project['id']}/todos",
        json={"title": "Other's todo", "due_date": "2026-10-05"},
        headers=other_auth_headers,
    )

    resp = client.get("/calendar", params={"from": "2026-10-01", "to": "2026-10-31"}, headers=auth_headers)
    assert resp.json()["todos"] == []
