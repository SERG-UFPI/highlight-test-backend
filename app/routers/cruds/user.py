from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import schemas, crud
from app.database import get_db
from app.helpers.user_utils import get_username_from_token, is_weak_password, is_valid_email
from app.security import get_token

router = APIRouter(
    prefix="/crud/user",
    tags=["user"],
    responses={404: {"description": "User not found"}},
)

@router.post("/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    if crud.user_exists(db, user.username):
        raise HTTPException(status_code=400, detail="User already exists")

    if user.password == "" or user.password != user.confirm_password:
        raise HTTPException(status_code=400, detail="Invalid password or password confirmation")

    if is_weak_password(user.password):
        raise HTTPException(status_code=400,
                            detail="Password is too weak. It must have at least 8 characters, including uppercase, lowercase, numbers, and special characters")

    if user.email != "" and not is_valid_email(user.email):
        raise HTTPException(status_code=400, detail="Invalid email format")

    return crud.create_user(db=db, user=user)

@router.get("/{username}/active", response_model=schemas.User)
def read_user_by_username_active(username: str, db: Session = Depends(get_db), token: str = Depends(get_token)):
    username_from_token = get_username_from_token(token)
    if username != username_from_token:
        raise HTTPException(status_code=404, detail="User not found")

    db_user = crud.get_user_by_username_active(db, username=username)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")

    return db_user

@router.get("/get_user", response_model=schemas.User)
def get_user(db: Session = Depends(get_db), token: str = Depends(get_token)):
    username_from_token = get_username_from_token(token)
    db_user = crud.get_user_by_username_active(db, username=username_from_token)

    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")

    if db_user.username != username_from_token:
        raise HTTPException(status_code=404, detail="User not found")

    return db_user

@router.get("/{user_id}", response_model=schemas.User)
def read_user_by_id(user_id: str, db: Session = Depends(get_db), token: str = Depends(get_token)):
    username_from_token = get_username_from_token(token)
    db_user = crud.get_user_by_id(db, user_id=user_id)

    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")

    if db_user.username != username_from_token:
        raise HTTPException(status_code=404, detail="User not found")

    return db_user

@router.put("/{user_id}", response_model=schemas.User)
def update_user(user_id: str, user: schemas.UserUpdate, db: Session = Depends(get_db), token: str = Depends(get_token)):
    username_from_token = get_username_from_token(token)

    db_user = crud.get_user_by_id(db, user_id=user_id)
    if db_user.username != username_from_token:
        raise HTTPException(status_code=404, detail="User not found")

    return crud.update_user(db=db, user_id=user_id, user=user)
