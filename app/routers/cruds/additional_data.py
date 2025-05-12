from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import schemas, crud
from app.database import get_db
from app.helpers.user_utils import get_username_from_token
from app.security import get_token, can_create, can_edit, can_delete

router = APIRouter(
    prefix="/crud/additional_data",
    tags=["additional_data"],
    responses={404: {"description": "AdditionalData not found"}},
)

@router.post("/", response_model=schemas.AdditionalData)
def create_additional_data(
    additional_data: schemas.AdditionalDataCreate, db: Session = Depends(get_db), token: str = Depends(get_token)
):
    username = get_username_from_token(token)
    db_repository = crud.get_repository_by_id(db, repository_id=str(additional_data.repository))
    if db_repository is None:
        raise HTTPException(status_code=404, detail="Repository not found")

    if not can_create(db_repository, username):
        raise HTTPException(status_code=403, detail="Not authorized to create this additional data")

    return crud.create_additional_data(db=db, additional_data=additional_data)


@router.get("/", response_model=list[schemas.AdditionalData])
def read_additional_data(skip: int = 0, limit: int = 1000, db: Session = Depends(get_db)):
    additional_data = crud.get_additional_data(db, skip=skip, limit=limit)
    return additional_data

@router.get("/{additional_data_id}", response_model=schemas.AdditionalData)
def read_additional_data_by_id(additional_data_id: str, db: Session = Depends(get_db)):
    db_additional_data = crud.get_additional_data_by_id(db, additional_data_id=additional_data_id)
    if db_additional_data is None:
        raise HTTPException(status_code=404, detail="AdditionalData not found")
    return db_additional_data

@router.get("/repository/{repository_id}", response_model=schemas.AdditionalData)
def read_additional_data_by_repository(repository_id: str, db: Session = Depends(get_db)):
    db_additional_data = crud.get_additional_data_by_repository(db, repository_id=repository_id)
    if db_additional_data is None:
        raise HTTPException(status_code=404, detail="AdditionalData not found")
    return db_additional_data

@router.put("/{additional_data_id}", response_model=schemas.AdditionalData)
def update_additional_data(
    additional_data_id: str, additional_data: schemas.AdditionalDataUpdate, db: Session = Depends(get_db), token: str = Depends(get_token)
):
    username = get_username_from_token(token)
    db_repository = crud.get_repository_by_id_and_username(db, repository_id=str(additional_data.repository), username=username)
    if db_repository is None:
        raise HTTPException(status_code=404, detail="Repository not found")

    if not can_edit(db_repository, username):
        raise HTTPException(status_code=403, detail="Not authorized to update this additional data")

    db_additional_data = crud.get_additional_data_by_id(db, additional_data_id=additional_data_id)
    if db_additional_data is None:
        raise HTTPException(status_code=404, detail="Additional data not found")

    return crud.update_additional_data(db=db, additional_data_id=additional_data_id, additional_data=additional_data)

@router.delete("/{additional_data_id}")
def delete_additional_data(additional_data_id: str, db: Session = Depends(get_db), token: str = Depends(get_token)):
    username = get_username_from_token(token)

    db_additional_data = crud.get_additional_data_by_id(db, additional_data_id=additional_data_id)
    if db_additional_data is None:
        raise HTTPException(status_code=404, detail="Additional data not found")

    db_repository = crud.get_repository_by_id_and_username(db, repository_id=db_additional_data.repository, username=username)
    if db_repository is None:
        raise HTTPException(status_code=404, detail="Repository not found")

    if not can_delete(db_repository, username):
        raise HTTPException(status_code=403, detail="Not authorized to delete this pipeline")

    crud.delete_additional_data(db=db, additional_data_id=additional_data_id)
    return {}