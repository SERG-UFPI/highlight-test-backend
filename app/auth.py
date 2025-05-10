from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from pydantic import BaseModel

from app.config import *

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

class TokenData(BaseModel):
    username: str | None = None

def verify_token(token: str, credentials_exception):
    try:
        payload = jwt.decode(token, AUTH_SECRET_KEY, algorithms=[AUTH_ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    return token_data

def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    return verify_token(token, credentials_exception)