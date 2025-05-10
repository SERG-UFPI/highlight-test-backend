from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import schemas, crud
from app.database import get_db
from app.helpers.user_utils import get_username_from_token
from app.security import get_token, can_edit

router = APIRouter(
    prefix="/crud/term",
    tags=["term"],
    responses={404: {"description": "Pipeline not found"}},
)

@router.post("/", status_code=status.HTTP_202_ACCEPTED)
def share_consent_pipeline(term: schemas.TermBase, db: Session = Depends(get_db), token: str = Depends(get_token)):
    username = get_username_from_token(token)
    db_repository = crud.get_repository_by_id_and_username(db, repository_id=term.repository_id, username=username)
    if db_repository is None:
        raise HTTPException(status_code=404, detail="Repository not found")

    db_pipeline = crud.get_pipeline_by_id(db, pipeline_id=term.pipeline_id)
    if db_pipeline is None:
        raise HTTPException(status_code=404, detail="Pipeline not found")

    if db_pipeline.repository != db_repository.id:
        raise HTTPException(
            status_code=400,
            detail="Incorrect repository or pipeline",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not can_edit(db_repository, username):
        raise HTTPException(status_code=403, detail="Not authorized to update this pipeline's share")

    crud.share_consent_pipeline(db=db, pipeline_id=term.pipeline_id, share_consent=term.share_consent)

    return {}
