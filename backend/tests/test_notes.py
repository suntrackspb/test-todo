def _create_project(client, headers, title="Project"):
    return client.post("/projects", json={"title": title}, headers=headers).json()


def test_create_and_list_notes(client, auth_headers):
    project = _create_project(client, auth_headers)
    resp = client.post(
        f"/projects/{project['id']}/notes",
        json={"title": "Note 1", "content_json": '{"text": "hello"}'},
        headers=auth_headers,
    )
    assert resp.status_code == 201
    assert resp.json()["title"] == "Note 1"

    list_resp = client.get(f"/projects/{project['id']}/notes", headers=auth_headers)
    assert list_resp.status_code == 200
    assert len(list_resp.json()) == 1


def test_update_note_content_and_due_date(client, auth_headers):
    project = _create_project(client, auth_headers)
    note = client.post(f"/projects/{project['id']}/notes", json={"title": "N"}, headers=auth_headers).json()

    resp = client.patch(
        f"/notes/{note['id']}",
        json={"content_json": '{"text": "updated"}', "due_date": "2026-10-01"},
        headers=auth_headers,
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["content_json"] == '{"text": "updated"}'
    assert body["due_date"] == "2026-10-01"


def test_clear_due_date(client, auth_headers):
    project = _create_project(client, auth_headers)
    note = client.post(
        f"/projects/{project['id']}/notes",
        json={"title": "N", "due_date": "2026-10-01"},
        headers=auth_headers,
    ).json()

    resp = client.patch(f"/notes/{note['id']}", json={"clear_due_date": True}, headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["due_date"] is None


def test_delete_note(client, auth_headers):
    project = _create_project(client, auth_headers)
    note = client.post(f"/projects/{project['id']}/notes", json={"title": "N"}, headers=auth_headers).json()

    del_resp = client.delete(f"/notes/{note['id']}", headers=auth_headers)
    assert del_resp.status_code == 204
    assert client.get(f"/notes/{note['id']}", headers=auth_headers).status_code == 404


def test_delete_note_removes_attachment_files(client, auth_headers):
    from app.core.config import settings

    project = _create_project(client, auth_headers)
    note = client.post(f"/projects/{project['id']}/notes", json={"title": "N"}, headers=auth_headers).json()

    upload_resp = client.post(
        f"/notes/{note['id']}/attachments",
        files={"file": ("pic.png", b"\x89PNG\r\n\x1a\n", "image/png")},
        headers=auth_headers,
    )
    assert upload_resp.status_code == 201
    relative_path = upload_resp.json()["file_path"]
    file_path = settings.uploads_dir / relative_path
    assert file_path.is_file()

    del_resp = client.delete(f"/notes/{note['id']}", headers=auth_headers)
    assert del_resp.status_code == 204
    assert not file_path.exists()


def test_cannot_access_notes_of_other_users_project(client, auth_headers, other_auth_headers):
    project = _create_project(client, auth_headers)
    note = client.post(f"/projects/{project['id']}/notes", json={"title": "N"}, headers=auth_headers).json()

    resp = client.get(f"/notes/{note['id']}", headers=other_auth_headers)
    assert resp.status_code == 404


def test_create_note_in_nonexistent_project(client, auth_headers):
    resp = client.post("/projects/9999/notes", json={"title": "N"}, headers=auth_headers)
    assert resp.status_code == 404
