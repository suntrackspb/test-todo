from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.deps import get_current_user
from app.database import get_db
from app.models import Note, Project, User
from app.schemas.schemas import NoteCreate, NoteOut, NoteUpdate

router = APIRouter(tags=["notes"])


def _get_owned_project(db: Session, project_id: int, user: User) -> Project:
    project = db.get(Project, project_id)
    if project is None or project.owner_id != user.id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Project not found")
    return project


def _get_owned_note(db: Session, note_id: int, user: User) -> Note:
    note = db.get(Note, note_id)
    if note is None or note.project.owner_id != user.id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Note not found")
    return note


@router.get("/projects/{project_id}/notes", response_model=list[NoteOut])
def list_notes(project_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    _get_owned_project(db, project_id, user)
    return db.query(Note).filter(Note.project_id == project_id).order_by(Note.updated_at.desc()).all()


@router.post("/projects/{project_id}/notes", response_model=NoteOut, status_code=status.HTTP_201_CREATED)
def create_note(
    project_id: int,
    payload: NoteCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    _get_owned_project(db, project_id, user)
    note = Note(
        project_id=project_id,
        title=payload.title,
        content_json=payload.content_json,
        note_type=payload.note_type,
        due_date=payload.due_date,
    )
    db.add(note)
    db.commit()
    db.refresh(note)
    return note


@router.get("/notes/{note_id}", response_model=NoteOut)
def get_note(note_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return _get_owned_note(db, note_id, user)


@router.patch("/notes/{note_id}", response_model=NoteOut)
def update_note(
    note_id: int,
    payload: NoteUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    note = _get_owned_note(db, note_id, user)

    if payload.title is not None:
        note.title = payload.title
    if payload.content_json is not None:
        note.content_json = payload.content_json
    if payload.clear_due_date:
        note.due_date = None
    elif payload.due_date is not None:
        note.due_date = payload.due_date

    db.commit()
    db.refresh(note)
    return note


@router.delete("/notes/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_note(note_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    note = _get_owned_note(db, note_id, user)
    attachment_paths = [attachment.file_path for attachment in note.attachments]

    db.delete(note)
    db.commit()

    for relative_path in attachment_paths:
        file_path = settings.uploads_dir / relative_path
        file_path.unlink(missing_ok=True)
