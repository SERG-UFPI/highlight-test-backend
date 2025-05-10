import uuid
from sqlalchemy import Column, ForeignKey, Integer, DateTime, Enum, func, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from .database import Base
from .enums import StatusEnum, UserStatusEnum
from .schemas import LanguageEnum
from .schemas import StageEnum
from sqlalchemy.types import TypeDecorator, String

class HttpUrlString(TypeDecorator):
    impl = String

    def process_bind_param(self, value, dialect):
        if value is not None:
            return str(value)
        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            return value
        return value

class Repository(Base):
    __tablename__ = "repository"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    owner = Column(String, nullable=False)
    default_branch = Column(String, nullable=False)
    clone_url = Column(HttpUrlString, nullable=False)
    registration_date = Column(DateTime(timezone=True), default=func.now(), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=True)


class AdditionalData(Base):
    __tablename__ = "additional_data"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    repository = Column(UUID(as_uuid=True), ForeignKey("repository.id"), nullable=False) # UUID for FK
    name = Column(String, nullable=True)
    full_name = Column(String, nullable=True)
    language = Column(Enum(LanguageEnum), nullable=True)
    forks_count = Column(Integer, nullable=True)
    open_issues_count = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), default=func.now(), nullable=True, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=True)
    pushed_at = Column(DateTime, nullable=True)
    external_id = Column(String, nullable=True)
    uses_external_id = Column(Boolean, nullable=True, default=False)

    repository_relation = relationship("Repository")

class Pipeline(Base):
    __tablename__ = "pipeline"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    repository = Column(UUID(as_uuid=True), ForeignKey("repository.id"), nullable=False) # UUID for FK
    created_at = Column(DateTime(timezone=True), default=func.now(), nullable=True, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=True)
    stage = Column(Enum(StageEnum), nullable=True)
    status = Column(Enum(StatusEnum), nullable=True)
    share_consent = Column(Boolean, nullable=True, default=False)

    repository_relation = relationship("Repository")

class User(Base):
    __tablename__ = "user"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    username = Column(String, nullable=False, unique=True)
    hashed_password = Column(String, nullable=False)
    fullname = Column(String, nullable=True)
    email = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), default=func.now(), nullable=True, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=True)
    status = Column(Enum(UserStatusEnum), nullable=True)
    github_user = Column(Boolean, nullable=True, default=False)
    github_token = Column(String, nullable=True)
