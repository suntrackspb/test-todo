from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.database import get_db
from app.models import Note, Project, Todo, User
from app.schemas.schemas import CalendarNoteItem, CalendarResponse, CalendarTodoItem

router = APIRouter(tags=["calendar"])


@router.get("/calendar", response_model=CalendarResponse)
def get_calendar(
    date_from: date = Query(alias="from"),
    date_to: date = Query(alias="to"),
    project_id: int | None = Query(default=None),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    if date_to < date_from:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="'to' must not be before 'from'")

    owned_project_ids = [p.id for p in db.query(Project.id).filter(Project.owner_id == user.id).all()]

    if project_id is not None:
        if project_id not in owned_project_ids:
            raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Project not found")
        owned_project_ids = [project_id]

    todos = (
        db.query(Todo)
        .filter(
            Todo.project_id.in_(owned_project_ids),
            Todo.due_date.isnot(None),
            Todo.due_date >= date_from,
            Todo.due_date <= date_to,
            Todo.status != "done",
        )
        .all()
    )
    notes = (
        db.query(Note)
        .filter(
            Note.project_id.in_(owned_project_ids),
            Note.due_date.isnot(None),
            Note.due_date >= date_from,
            Note.due_date <= date_to,
        )
        .all()
    )

    return CalendarResponse(
        todos=[
            CalendarTodoItem(
                id=t.id,
                project_id=t.project_id,
                title=t.title,
                status=t.status,
                priority=t.priority,
                due_date=t.due_date,
            )
            for t in todos
        ],
        notes=[
            CalendarNoteItem(id=n.id, project_id=n.project_id, title=n.title, due_date=n.due_date)
            for n in notes
        ],
    )
