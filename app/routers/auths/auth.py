import httpx
from fastapi import APIRouter, Depends, HTTPException
from datetime import timedelta
from requests import Session
from starlette.responses import RedirectResponse

from app import crud
from app.config import *
from app.helpers.user_utils import check_password, create_access_token
from app import schemas
from app.database import get_db
from app.helpers.utils import parse_int

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
    responses={404: {"description": "User not found"}},
)

@router.post("/token")
async def login_for_access_token(form_data: schemas.UserBase, db: Session = Depends(get_db)):
    user_db = crud.get_user_by_username_active(db=db, username=form_data.username)
    if not user_db:
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not (form_data.password != "" and check_password(form_data.password, user_db.hashed_password)):
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=parse_int(AUTH_ACCESS_TOKEN_EXPIRE_MINUTES))
    access_token = create_access_token(
        data={"sub": user_db.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/github")
def login_with_github():
    github_auth_url = (
        f"https://github.com/login/oauth/authorize"
        f"?client_id={GITHUB_CLIENT_ID}&redirect_uri={GITHUB_REDIRECT_URI}&scope=user"
    )
    return RedirectResponse(github_auth_url)

@router.get("/github/callback")
async def github_callback(code: str):
    token_url = "https://github.com/login/oauth/access_token"
    headers = {"Accept": "application/json"}
    payload = {
        "client_id": GITHUB_CLIENT_ID,
        "client_secret": GITHUB_CLIENT_SECRET,
        "code": code,
        "redirect_uri": GITHUB_REDIRECT_URI,
    }

    async with httpx.AsyncClient() as client:
        token_response = await client.post(token_url, headers=headers, data=payload)
        token_data = token_response.json()

    if "access_token" not in token_data:
        raise HTTPException(status_code=400, detail="Failed to retrieve access token")

    access_token = token_data["access_token"]

    user_url = "https://api.github.com/user"
    user_headers = {"Authorization": f"Bearer {access_token}"}

    async with httpx.AsyncClient() as client:
        user_response = await client.get(user_url, headers=user_headers)
        user_data = user_response.json()

    db = next(get_db())
    crud.save_integration_user(db=db, username=str(user_data["login"]), github_token=str(access_token))

    return RedirectResponse(url=GITHUB_REDIRECT_FRONTEND+"?token="+access_token, status_code=302)

@router.post("/login_by_token")
async def login_by_token(form_data: schemas.IntegrationUserBase, db: Session = Depends(get_db)):
    user_db = crud.get_user_by_token_active(db=db, token=form_data.token)
    if not user_db:
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=parse_int(AUTH_ACCESS_TOKEN_EXPIRE_MINUTES))
    access_token = create_access_token(
        data={"sub": user_db.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

