from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import schemas, crud
from app.database import get_db
from app.helpers.user_utils import get_username_from_token
from app.security import get_token, can_edit, can_delete
from fastapi_pagination import Page, paginate

router = APIRouter(
    prefix="/crud/repository",
    tags=["repository"],
    responses={404: {"description": "Repository not found"}},
)

@router.post("/", response_model=schemas.Repository)
def create_repository(repository: schemas.RepositoryCreate, db: Session = Depends(get_db), token: str = Depends(get_token)):
    username = get_username_from_token(token)
    return crud.create_repository(db=db, repository=repository, username=username)


@router.get("/", response_model=Page[schemas.Repository])
def read_repositories(skip: int = 0, limit: int = 1000, clone_url: Optional[str] = None,  db: Session = Depends(get_db), token: str = Depends(get_token)):
    username = get_username_from_token(token)
    repositories = crud.get_repositories_by_username(db, username, clone_url, skip=skip, limit=limit)
    return paginate(repositories)


@router.get("/{repository_id}", response_model=schemas.Repository)
def read_repository_by_id(repository_id: str, db: Session = Depends(get_db), token: str = Depends(get_token)):
    username = get_username_from_token(token)
    db_repository = crud.get_repository_by_id_and_username(db, repository_id=repository_id, username=username)
    if db_repository is None:
        raise HTTPException(status_code=404, detail="Repository not found")
    return db_repository

@router.put("/{repository_id}", response_model=schemas.Repository)
def update_repository(repository_id: str, repository: schemas.RepositoryUpdate, db: Session = Depends(get_db), token: str = Depends(get_token)):
    username = get_username_from_token(token)
    db_repository = crud.get_repository_by_id_and_username(db, repository_id=repository_id, username=username)
    if db_repository is None:
        raise HTTPException(status_code=404, detail="Repository not found")

    if not can_edit(db_repository, username):
        raise HTTPException(status_code=403, detail="Not authorized to update this repository")

    return crud.update_repository(db=db, repository_id=repository_id, repository=repository)

@router.delete("/{repository_id}")
def delete_repository(repository_id: str, db: Session = Depends(get_db), token: str = Depends(get_token)):
    username = get_username_from_token(token)
    db_repository = crud.get_repository_by_id_and_username(db, repository_id=repository_id, username=username)
    if db_repository is None:
        raise HTTPException(status_code=404, detail="Repository not found")

    if not can_delete(db_repository, username):
        raise HTTPException(status_code=403, detail="Not authorized to delete this repository")

    crud.delete_repository(db=db, repository_id=repository_id)
    return {}