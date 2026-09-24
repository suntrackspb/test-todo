from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict


# ---- Auth ----
class LoginRequest(BaseModel):
    login: str
    password: str


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    refresh_token: str


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    login: str
    display_name: str


# ---- Projects ----
class ProjectCreate(BaseModel):
    title: str
    parent_id: int | None = None
    order: int = 0


class ProjectUpdate(BaseModel):
    title: str | None = None
    parent_id: int | None = None
    order: int | None = None


class ProjectOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    title: str
    parent_id: int | None
    order: int
    created_at: datetime


class ProjectTreeNode(ProjectOut):
    children: list["ProjectTreeNode"] = []


# ---- Notes ----
class NoteCreate(BaseModel):
    title: str = ""
    content_json: str = "{}"
    note_type: Literal["text", "drawing"] = "text"
    due_date: date | None = None


class NoteUpdate(BaseModel):
    title: str | None = None
    content_json: str | None = None
    due_date: date | None = None
    clear_due_date: bool = False


class AttachmentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    file_path: str
    mime_type: str
    kind: str
    created_at: datetime


class NoteOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    project_id: int
    title: str
    content_json: str
    note_type: str
    due_date: date | None
    created_at: datetime
    updated_at: datetime
    attachments: list[AttachmentOut] = []


TodoPriority = Literal["critical", "urgent", "low", "none"]


# ---- Todos ----
class TodoCreate(BaseModel):
    title: str
    status: Literal["todo", "in_progress", "done"] = "todo"
    priority: TodoPriority = "none"
    due_date: date | None = None
    note_id: int | None = None
    order: int = 0


class TodoUpdate(BaseModel):
    title: str | None = None
    status: Literal["todo", "in_progress", "done"] | None = None
    priority: TodoPriority | None = None
    due_date: date | None = None
    clear_due_date: bool = False
    order: int | None = None


class TodoOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    project_id: int
    note_id: int | None
    title: str
    status: str
    priority: str
    due_date: date | None
    order: int
    created_at: datetime


# ---- Calendar ----
class CalendarTodoItem(BaseModel):
    id: int
    project_id: int
    title: str
    status: str
    priority: str
    due_date: date


class CalendarNoteItem(BaseModel):
    id: int
    project_id: int
    title: str
    due_date: date


class CalendarResponse(BaseModel):
    todos: list[CalendarTodoItem]
    notes: list[CalendarNoteItem]
