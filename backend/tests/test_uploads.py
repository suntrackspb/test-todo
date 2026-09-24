import io

import pytest

from app.core.config import settings


def _create_note(client, headers):
    project = client.post("/projects", json={"title": "P"}, headers=headers).json()
    return client.post(f"/projects/{project['id']}/notes", json={"title": "N"}, headers=headers).json()


PNG_BYTES = (
    b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
    b"\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x01"
    b"\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82"
)


@pytest.fixture(autouse=True)
def _isolate_uploads_dir(tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "uploads_dir", tmp_path)


def test_upload_valid_image(client, auth_headers):
    note = _create_note(client, auth_headers)
    files = {"file": ("drawing.png", io.BytesIO(PNG_BYTES), "image/png")}
    resp = client.post(f"/notes/{note['id']}/attachments", files=files, headers=auth_headers)
    assert resp.status_code == 201
    body = resp.json()
    assert body["mime_type"] == "image/png"
    assert (settings.uploads_dir / body["file_path"]).exists()


def test_upload_rejects_bad_mime_type(client, auth_headers):
    note = _create_note(client, auth_headers)
    files = {"file": ("evil.exe", io.BytesIO(b"not an image"), "application/x-msdownload")}
    resp = client.post(f"/notes/{note['id']}/attachments", files=files, headers=auth_headers)
    assert resp.status_code == 400


def test_upload_rejects_oversized_file(client, auth_headers, monkeypatch):
    monkeypatch.setattr(settings, "max_upload_size_bytes", 10)
    note = _create_note(client, auth_headers)
    files = {"file": ("big.png", io.BytesIO(PNG_BYTES), "image/png")}
    resp = client.post(f"/notes/{note['id']}/attachments", files=files, headers=auth_headers)
    assert resp.status_code == 400


def test_upload_to_other_users_note_forbidden(client, auth_headers, other_auth_headers):
    note = _create_note(client, auth_headers)
    files = {"file": ("drawing.png", io.BytesIO(PNG_BYTES), "image/png")}
    resp = client.post(f"/notes/{note['id']}/attachments", files=files, headers=other_auth_headers)
    assert resp.status_code == 404


def test_get_uploaded_file_back(client, auth_headers):
    note = _create_note(client, auth_headers)
    files = {"file": ("drawing.png", io.BytesIO(PNG_BYTES), "image/png")}
    upload_resp = client.post(f"/notes/{note['id']}/attachments", files=files, headers=auth_headers)
    file_path = upload_resp.json()["file_path"]

    get_resp = client.get(f"/uploads/{file_path}", headers=auth_headers)
    assert get_resp.status_code == 200
    assert get_resp.content == PNG_BYTES


def test_get_uploaded_file_via_query_token(client, auth_headers):
    note = _create_note(client, auth_headers)
    files = {"file": ("drawing.png", io.BytesIO(PNG_BYTES), "image/png")}
    upload_resp = client.post(f"/notes/{note['id']}/attachments", files=files, headers=auth_headers)
    file_path = upload_resp.json()["file_path"]
    token = auth_headers["Authorization"].split(" ")[1]

    get_resp = client.get(f"/uploads/{file_path}", params={"token": token})
    assert get_resp.status_code == 200
    assert get_resp.content == PNG_BYTES


def test_get_uploaded_file_without_credentials_rejected(client, auth_headers):
    note = _create_note(client, auth_headers)
    files = {"file": ("drawing.png", io.BytesIO(PNG_BYTES), "image/png")}
    upload_resp = client.post(f"/notes/{note['id']}/attachments", files=files, headers=auth_headers)
    file_path = upload_resp.json()["file_path"]

    get_resp = client.get(f"/uploads/{file_path}")
    assert get_resp.status_code == 401
