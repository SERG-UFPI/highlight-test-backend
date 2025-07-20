from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.helpers.user_utils import get_username_or_empty
from app.security import get_token, check_permission
from app import crud

router = APIRouter(
    prefix="/permissions",
    tags=["permissions"],
    responses={404: {"description": "Permission not found"}},
)

@router.get("/{repository_id}")
def get_permissions(repository_id: str, db: Session = Depends(get_db), token: str = Depends(get_token)):
    username = get_username_or_empty(token)
    db_repository = crud.get_repository_by_id_and_username(db, repository_id=repository_id, username=username)
    if db_repository is None:
        raise HTTPException(status_code=404, detail="Repository not found")

    return check_permission(db_repository, username)