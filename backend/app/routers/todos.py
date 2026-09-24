from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.database import get_db
from app.models import Project, Todo, User
from app.schemas.schemas import TodoCreate, TodoOut, TodoUpdate

router = APIRouter(tags=["todos"])


def _get_owned_project(db: Session, project_id: int, user: User) -> Project:
    project = db.get(Project, project_id)
    if project is None or project.owner_id != user.id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Project not found")
    return project


def _get_owned_todo(db: Session, todo_id: int, user: User) -> Todo:
    todo = db.get(Todo, todo_id)
    if todo is None or todo.project.owner_id != user.id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Todo not found")
    return todo


@router.get("/projects/{project_id}/todos", response_model=list[TodoOut])
def list_todos(
    project_id: int,
    status_filter: str | None = Query(default=None, alias="status"),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    _get_owned_project(db, project_id, user)
    query = db.query(Todo).filter(Todo.project_id == project_id)
    if status_filter is not None:
        query = query.filter(Todo.status == status_filter)
    return query.order_by(Todo.order).all()


@router.post("/projects/{project_id}/todos", response_model=TodoOut, status_code=status.HTTP_201_CREATED)
def create_todo(
    project_id: int,
    payload: TodoCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    _get_owned_project(db, project_id, user)
    todo = Todo(
        project_id=project_id,
        note_id=payload.note_id,
        title=payload.title,
        status=payload.status,
        priority=payload.priority,
        due_date=payload.due_date,
        order=payload.order,
    )
    db.add(todo)
    db.commit()
    db.refresh(todo)
    return todo


@router.patch("/todos/{todo_id}", response_model=TodoOut)
def update_todo(
    todo_id: int,
    payload: TodoUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    todo = _get_owned_todo(db, todo_id, user)

    if payload.title is not None:
        todo.title = payload.title
    if payload.status is not None:
        todo.status = payload.status
    if payload.priority is not None:
        todo.priority = payload.priority
    if payload.clear_due_date:
        todo.due_date = None
    elif payload.due_date is not None:
        todo.due_date = payload.due_date
    if payload.order is not None:
        todo.order = payload.order

    db.commit()
    db.refresh(todo)
    return todo


@router.delete("/todos/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_todo(todo_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    todo = _get_owned_todo(db, todo_id, user)
    db.delete(todo)
    db.commit()
