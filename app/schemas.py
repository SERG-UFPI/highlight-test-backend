from pydantic import BaseModel, HttpUrl
from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy import Boolean

from app.enums import LanguageEnum, StageEnum, StatusEnum, UserStatusEnum


class RepositoryBase(BaseModel):
    default_branch: str
    clone_url: HttpUrl

class RepositoryCreate(RepositoryBase):
    pass

class RepositoryUpdate(RepositoryBase):
    pass


class Repository(RepositoryBase):
    id: UUID
    registration_date: datetime
    updated_at: Optional[datetime] = None
    owner: str

    class Config:
        from_attributes = True


class AdditionalDataBase(BaseModel):
    repository: UUID
    name: Optional[str] = None
    full_name: Optional[str] = None
    language: Optional[LanguageEnum] = None
    forks_count: Optional[int] = None
    open_issues_count: Optional[int] = None
    created_at: Optional[datetime] = None
    pushed_at: Optional[datetime] = None
    external_id: Optional[str] = None


class AdditionalDataCreate(AdditionalDataBase):
    pass

class AdditionalDataUpdate(AdditionalDataBase):
    pass

class AdditionalData(AdditionalDataBase):
    id: UUID
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class PipelineBase(BaseModel):
    repository: UUID
    stage: Optional[StageEnum] = None
    status: Optional[StatusEnum] = None

class PipelineCreate(PipelineBase):
    pass

class PipelineUpdate(PipelineBase):
    pass

class Pipeline(PipelineBase):
    id: UUID
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    share_consent: Optional[bool] = None

    class Config:
        from_attributes = True

class ProcessBase(BaseModel):
    pipeline_id: str

class ProcessRevision(ProcessBase):
    revision: str

class UserBase(BaseModel):
    username: str
    password: str
    fullname: Optional[str] = None
    email: Optional[str] = None

class UserCreate(UserBase):
    confirm_password: str
    pass

class UserUpdate(UserBase):
    pass

class User(BaseModel):
    id: UUID
    username: str
    fullname: Optional[str] = None
    email: Optional[str] = None
    status: Optional[UserStatusEnum] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    github_user: Optional[bool] = None
    github_token: Optional[str] = None

    class Config:
        from_attributes = True

class IntegrationUserBase(BaseModel):
    token: str

class TermBase(BaseModel):
    repository_id: str
    pipeline_id: str
    share_consent: bool
