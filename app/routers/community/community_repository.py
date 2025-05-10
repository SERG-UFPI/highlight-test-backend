from typing import Optional

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app import schemas, crud
from app.database import get_db
from fastapi_pagination import Page, paginate, LimitOffsetPage

router = APIRouter(
    prefix="/community/repository",
    tags=["community_repository"],
    responses={404: {"description": "Repository not found"}},
)

@router.get("/", response_model=Page[schemas.Repository])
def read_repositories(skip: int = 0, limit: int = 1000, clone_url: Optional[str] = None,  db: Session = Depends(get_db)):
    repositories = crud.get_shared_repositories(db, clone_url, skip=skip, limit=limit)
    return paginate(repositories)