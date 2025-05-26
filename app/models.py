import uuid
from sqlalchemy import Column, ForeignKey, Integer, DateTime, Enum, func, Boolean, Text, JSON, Float
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

class Commit(Base):
    __tablename__ = "commits"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    hash = Column(String, nullable=False)
    author_name = Column(String, nullable=False)
    committer_name = Column(String, nullable=False)
    author_date = Column(DateTime, nullable=False)
    message = Column(Text, nullable=False)
    pipeline_id = Column(UUID(as_uuid=True), ForeignKey("pipeline.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), default=func.now(), nullable=True, server_default=func.now())

class Competence(Base):
    __tablename__ = "competences"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    competence = Column(String, nullable=False)
    pipeline_id = Column(UUID(as_uuid=True), ForeignKey("pipeline.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), default=func.now(), nullable=True, server_default=func.now())


class BaseItem(Base):
    __tablename__ = "base_items"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    base_item = Column(String, nullable=False)
    pipeline_id = Column(UUID(as_uuid=True), ForeignKey("pipeline.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), default=func.now(), nullable=True, server_default=func.now())

class TestData(Base):
    __tablename__ = "test_data"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    file_path = Column(String, nullable=False)
    is_test_file = Column(Boolean, nullable=False)
    has_test_import = Column(Boolean, nullable=False)
    has_test_call = Column(Boolean, nullable=False)
    pipeline_id = Column(UUID(as_uuid=True), ForeignKey("pipeline.id"), nullable=False)
    commit_order = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), default=func.now(), nullable=True, server_default=func.now())

class CodeMetrics(Base):
    __tablename__ = "code_metrics"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    full_name = Column(String, nullable=False)
    timeseries = Column(JSON, nullable=False)
    metric_type = Column(String, nullable=False)  # 'production' ou 'test'
    pipeline_id = Column(UUID(as_uuid=True), ForeignKey("pipeline.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)

class ProjectDimension(Base):
    __tablename__ = "project_dimensions"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    n_commits = Column(Integer, nullable=False)
    n_devs = Column(Integer, nullable=False)
    n_forks_count = Column(Integer, nullable=False)
    n_open_issues_count = Column(Integer, nullable=False)
    pipeline_id = Column(UUID(as_uuid=True), ForeignKey("pipeline.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)

class CommitMessageItem(Base):
    __tablename__ = "commit_message_items"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    hash = Column(String, nullable=False)  # A
    message = Column(Text, nullable=False)  # B
    bug_fix_regex_count = Column(Integer, nullable=True, default=0)  # C
    adaptive_regex_count = Column(Integer, nullable=True, default=0)  # D
    adaptive_by_negation_regex_count = Column(Integer, nullable=True, default=0)  # E
    perfective_regex_count = Column(Integer, nullable=True, default=0)  # F
    refactor_regex_count = Column(Integer, nullable=True, default=0)  # G
    is_perfective = Column(Boolean, nullable=True, default=False)  # H
    is_refactor = Column(Boolean, nullable=True, default=False)  # I
    is_adaptive = Column(Integer, nullable=True, default=False)  # J
    is_adaptive_by_negation = Column(Boolean, nullable=True, default=False)  # K
    is_corrective = Column(Boolean, nullable=True, default=False)  # L
    perfective_in_text = Column(JSON, nullable=True)  # M
    refactor_in_text = Column(JSON, nullable=True)  # N
    adaptive_in_text = Column(JSON, nullable=True)  # O
    adaptive_by_negation_in_text = Column(JSON, nullable=True)  # P
    corrective_in_text = Column(JSON, nullable=True)  # Q
    pipeline_id = Column(UUID(as_uuid=True), ForeignKey("pipeline.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)

class MaintenanceActivitySummary(Base):
    __tablename__ = "maintenance_activity_summaries"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    n_corrective = Column(Float, nullable=False)
    n_adaptive = Column(Float, nullable=False)
    n_perfective = Column(Float, nullable=False)
    n_multi = Column(Float, nullable=False)
    pipeline_id = Column(UUID(as_uuid=True), ForeignKey("pipeline.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)

class Correlation(Base):
    __tablename__ = "correlation"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    pearson_correlation = Column(Float, nullable=False)
    pipeline_id = Column(UUID(as_uuid=True), ForeignKey("pipeline.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)

class CodeDistributionDetail(Base):
    __tablename__ = "code_distribution_details"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    path = Column(String, nullable=False)
    loc = Column(Integer, nullable=False)
    commit_order = Column(Integer, nullable=False)
    language = Column(String, nullable=True)
    pipeline_id = Column(UUID(as_uuid=True), ForeignKey("pipeline.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)

class Insights(Base):
    __tablename__ = "insights"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    generated_text = Column(Text, nullable=False)
    pipeline_id = Column(UUID(as_uuid=True), ForeignKey("pipeline.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)
