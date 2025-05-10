from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

def get_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    if not credentials:
        raise HTTPException(status_code=401, detail="Token not provided")
    return credentials.credentials

def check_permission(db_repository: any, username: str):
    permission = {"view": True}

    if db_repository.owner != username:
        permission["create"] = False
        permission["edit"] = False
        permission["delete"] = False
    else:
        permission["create"] = True
        permission["edit"] = True
        permission["delete"] = True

    return permission

def can_view(db_repository: any, username: str):
    permission = check_permission(db_repository, username)

    return permission["view"]

def can_create(db_repository: any, username: str):
    permission = check_permission(db_repository, username)

    return permission["create"]

def can_edit(db_repository: any, username: str):
    permission = check_permission(db_repository, username)

    return permission["edit"]

def can_delete(db_repository: any, username: str):
    permission = check_permission(db_repository, username)

    return permission["delete"]
