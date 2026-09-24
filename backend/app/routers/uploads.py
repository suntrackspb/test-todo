import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.deps import get_current_user, get_current_user_from_header_or_query
from app.database import get_db
from app.models import Attachment, Note, User

router = APIRouter(tags=["uploads"])

ALLOWED_MIME_TYPES = {"image/png", "image/jpeg", "image/gif", "image/webp"}


def _get_owned_note(db: Session, note_id: int, user: User) -> Note:
    note = db.get(Note, note_id)
    if note is None or note.project.owner_id != user.id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Note not found")
    return note


@router.post("/notes/{note_id}/attachments", status_code=status.HTTP_201_CREATED)
async def upload_attachment(
    note_id: int,
    file: UploadFile,
    kind: str = "image",
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    note = _get_owned_note(db, note_id, user)

    if file.content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Unsupported file type")

    contents = await file.read()
    if len(contents) > settings.max_upload_size_bytes:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="File too large")

    user_dir = settings.uploads_dir / str(user.id)
    user_dir.mkdir(parents=True, exist_ok=True)

    ext = Path(file.filename or "").suffix or ".bin"
    stored_name = f"{uuid.uuid4().hex}{ext}"
    dest_path = user_dir / stored_name
    dest_path.write_bytes(contents)

    relative_path = f"{user.id}/{stored_name}"
    attachment = Attachment(
        note_id=note.id,
        file_path=relative_path,
        mime_type=file.content_type,
        kind=kind,
    )
    db.add(attachment)
    db.commit()
    db.refresh(attachment)
    return attachment


@router.get("/uploads/{user_id}/{filename}")
def get_upload(
    user_id: int,
    filename: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user_from_header_or_query),
):
    if user_id != user.id:
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail="Forbidden")

    file_path = settings.uploads_dir / str(user_id) / filename
    if not file_path.is_file():
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="File not found")
    return FileResponse(file_path)
