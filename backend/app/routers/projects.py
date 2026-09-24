from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.database import get_db
from app.models import Project, User
from app.schemas.schemas import ProjectCreate, ProjectOut, ProjectTreeNode, ProjectUpdate

router = APIRouter(prefix="/projects", tags=["projects"])


def _get_owned_project(db: Session, project_id: int, user: User) -> Project:
    project = db.get(Project, project_id)
    if project is None or project.owner_id != user.id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Project not found")
    return project


def _build_tree(projects: list[Project], parent_id: int | None) -> list[ProjectTreeNode]:
    nodes = []
    for project in projects:
        if project.parent_id != parent_id:
            continue
        node = ProjectTreeNode.model_validate(project)
        node.children = _build_tree(projects, project.id)
        nodes.append(node)
    return nodes


@router.get("", response_model=list[ProjectOut])
def list_projects(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return db.query(Project).filter(Project.owner_id == user.id).order_by(Project.order).all()


@router.get("/tree", response_model=list[ProjectTreeNode])
def get_tree(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    projects = db.query(Project).filter(Project.owner_id == user.id).order_by(Project.order).all()
    return _build_tree(projects, None)


@router.post("", response_model=ProjectOut, status_code=status.HTTP_201_CREATED)
def create_project(payload: ProjectCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    if payload.parent_id is not None:
        _get_owned_project(db, payload.parent_id, user)

    project = Project(
        owner_id=user.id,
        parent_id=payload.parent_id,
        title=payload.title,
        order=payload.order,
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


@router.get("/{project_id}", response_model=ProjectOut)
def get_project(project_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return _get_owned_project(db, project_id, user)


@router.patch("/{project_id}", response_model=ProjectOut)
def update_project(
    project_id: int,
    payload: ProjectUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    project = _get_owned_project(db, project_id, user)

    if payload.parent_id is not None:
        if payload.parent_id == project_id:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Project cannot be its own parent")
        _get_owned_project(db, payload.parent_id, user)
        project.parent_id = payload.parent_id
    if payload.title is not None:
        project.title = payload.title
    if payload.order is not None:
        project.order = payload.order

    db.commit()
    db.refresh(project)
    return project


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(project_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    project = _get_owned_project(db, project_id, user)
    db.delete(project)
    db.commit()
