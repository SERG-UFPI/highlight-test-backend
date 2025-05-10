import bcrypt
from fastapi import HTTPException
from datetime import datetime, timedelta
import jwt

from app.config import AUTH_SECRET_KEY, AUTH_ALGORITHM

def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt.
    :param password:
    :return:
    """
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed_password.decode('utf-8')

def check_password(password: str, hashed_password: str) -> bool:
    """
    Check if the provided password matches the hashed password.
    :param password:
    :param hashed_password:
    :return:
    """
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    """
    Create a JWT access token.
    :param data:
    :param expires_delta:
    :return:
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, AUTH_SECRET_KEY, algorithm=AUTH_ALGORITHM)
    return encoded_jwt

def get_username_from_token(token: str) -> str:
    """
    Extract the username from a JWT token.
    :param token:
    :return:
    """
    try:
        payload = jwt.decode(token, AUTH_SECRET_KEY, algorithms=[AUTH_ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return username
    except:
        raise HTTPException(status_code=401, detail="Invalid token")