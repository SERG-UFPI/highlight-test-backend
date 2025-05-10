from fastapi import APIRouter, Depends, HTTPException
from fastapi_pagination import Page, paginate
from sqlalchemy.orm import Session
from app import schemas, crud
from app.database import get_db
from app.helpers.user_utils import get_username_from_token
from app.security import get_token, can_create, can_edit, can_delete

router = APIRouter(
    prefix="/crud/pipeline",
    tags=["pipeline"],
    responses={404: {"description": "Pipeline not found"}},
)

@router.post("/", response_model=schemas.Pipeline)
def create_pipeline(
    pipeline: schemas.PipelineCreate, db: Session = Depends(get_db), token: str = Depends(get_token)
):
    username = get_username_from_token(token)
    db_repository = crud.get_repository_by_id(db, repository_id=str(pipeline.repository))
    if db_repository is None:
        raise HTTPException(status_code=404, detail="Repository not found")

    if not can_create(db_repository, username):
        raise HTTPException(status_code=403, detail="Not authorized to create this pipeline")

    return crud.create_pipeline(db=db, pipeline=pipeline)

@router.get("/", response_model=Page[schemas.Pipeline])
def read_pipelines(skip: int = 0, limit: int = 1000, db: Session = Depends(get_db)):
    pipelines = crud.get_pipelines(db, skip=skip, limit=limit)
    return paginate(pipelines)

@router.get("/repository/{repository_id}", response_model=Page[schemas.Pipeline])
def read_pipelines_by_repository(repository_id: str , skip: int = 0, limit: int = 1000, db: Session = Depends(get_db)):
    pipelines = crud.get_pipelines_by_repository(db, repository_id, skip=skip, limit=limit)
    return paginate(pipelines)

@router.get("/{pipeline_id}", response_model=schemas.Pipeline)
def read_pipeline_by_id(pipeline_id: str, db: Session = Depends(get_db)):
    db_pipeline = crud.get_pipeline_by_id(db, pipeline_id=pipeline_id)
    if db_pipeline is None:
        raise HTTPException(status_code=404, detail="Pipeline not found")
    return db_pipeline

@router.put("/{pipeline_id}", response_model=schemas.Pipeline)
def update_pipeline(
    pipeline_id: str, pipeline: schemas.PipelineUpdate, db: Session = Depends(get_db), token: str = Depends(get_token)
):
    username = get_username_from_token(token)
    db_repository = crud.get_repository_by_id_and_username(db, repository_id=str(pipeline.repository), username=username)
    if db_repository is None:
        raise HTTPException(status_code=404, detail="Repository not found")

    if not can_edit(db_repository, username):
        raise HTTPException(status_code=403, detail="Not authorized to update this pipeline")

    db_pipeline = crud.get_pipeline_by_id(db, pipeline_id=pipeline_id)
    if db_pipeline is None:
        raise HTTPException(status_code=404, detail="Pipeline not found")

    return crud.update_pipeline(db=db, pipeline_id=pipeline_id, pipeline=pipeline)

@router.delete("/{pipeline_id}")
def delete_pipeline(pipeline_id: str, db: Session = Depends(get_db), token: str = Depends(get_token)):
    username = get_username_from_token(token)

    db_pipeline = crud.get_pipeline_by_id(db, pipeline_id=pipeline_id)
    if db_pipeline is None:
        raise HTTPException(status_code=404, detail="Pipeline not found")

    db_repository = crud.get_repository_by_id_and_username(db, repository_id=db_pipeline.repository, username=username)
    if db_repository is None:
        raise HTTPException(status_code=404, detail="Repository not found")

    if not can_delete(db_repository, username):
        raise HTTPException(status_code=403, detail="Not authorized to delete this pipeline")

    crud.delete_pipeline(db=db, pipeline_id=pipeline_id)
    return {}
