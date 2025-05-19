import uuid

from sqlalchemy import and_, or_, func, desc
from sqlalchemy.orm import Session

from . import models, schemas
from datetime import datetime

from .enums import UserStatusEnum
from .helpers.user_utils import hash_password
from .models import Commit, Competence, BaseItem, TestData, CodeMetrics, ProjectDimension, CommitMessageItem, \
    MaintenanceActivitySummary, Correlation, Insights, CodeDistributionDetail

# repository
def get_repository_by_id(db: Session, repository_id: str):
    return db.query(models.Repository).filter(models.Repository.id == repository_id).first()

def get_repository_by_clone_url(db: Session, clone_url: str):
    return db.query(models.Repository).filter(models.Repository.clone_url == clone_url).first()

def get_repository_by_id_and_username(db: Session, repository_id: str, username: str):
    return (db.query(models.Repository)
            .join(models.Pipeline, models.Pipeline.repository == models.Repository.id)
            .filter(models.Repository.id == repository_id, or_(
                models.Repository.owner == username,
                models.Pipeline.share_consent == True
            )).first())

def get_repositories(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Repository).offset(skip).limit(limit).all()

def get_repositories_by_username(db: Session, username: str, clone_url: str, skip: int = 0, limit: int = 100):
    if clone_url:
        return db.query(models.Repository).filter(models.Repository.owner == username, and_(models.Repository.clone_url.ilike(f"%{clone_url}%"))).order_by(models.Repository.registration_date.desc()).offset(skip).limit(limit).all()

    return db.query(models.Repository).filter(models.Repository.owner == username).order_by(models.Repository.registration_date.desc()).offset(skip).limit(limit).all()

def get_shared_repositories(db: Session, clone_url: str, skip: int = 0, limit: int = 100):
    if clone_url:
        return (db.query(models.Repository).join(models.Pipeline, models.Pipeline.repository == models.Repository.id)
                .filter(models.Pipeline.share_consent == True, and_(models.Repository.clone_url.ilike(f"%{clone_url}%")))
                .order_by(models.Repository.registration_date.desc()).offset(skip).limit(limit).all())

    return (db.query(models.Repository).join(models.Pipeline, models.Pipeline.repository == models.Repository.id)
            .filter(models.Pipeline.share_consent == True).order_by(models.Repository.registration_date.desc()).offset(skip).limit(limit).all())


def create_repository(db: Session, repository: schemas.RepositoryCreate, username: str):
    db_repository = models.Repository(**repository.dict())
    db_repository.owner = username
    db.add(db_repository)
    db.commit()
    db.refresh(db_repository)
    return db_repository

def update_repository(db: Session, repository_id: str, repository: schemas.RepositoryUpdate):
    db_repository = db.query(models.Repository).filter(models.Repository.id == repository_id).first()
    db_repository.owner = repository.owner
    db_repository.default_branch = repository.default_branch
    db_repository.clone_url = repository.clone_url
    db_repository.additional_data = repository.additional_data
    db_repository.updated_at = datetime.now()
    db.commit()
    db.refresh(db_repository)
    return db_repository

def delete_repository(db: Session, repository_id: str):
    db.query(models.Repository).filter(models.Repository.id == repository_id).delete()
    db.commit()
    return True

# additional_data
def get_additional_data_by_repository(db: Session, repository_id: str):
    return db.query(models.AdditionalData).filter(models.AdditionalData.repository == repository_id).first()

def get_additional_data_by_id(db: Session, additional_data_id: str):
    return db.query(models.AdditionalData).filter(models.AdditionalData.id == additional_data_id).first()

def get_additional_data(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.AdditionalData).offset(skip).limit(limit).all()

def create_additional_data(db: Session, additional_data: schemas.AdditionalDataCreate):
    db_additional_data = models.AdditionalData(**additional_data.dict())
    db.add(db_additional_data)
    db.commit()
    db.refresh(db_additional_data)
    return db_additional_data

def update_additional_data(db: Session, additional_data_id: str, additional_data: schemas.AdditionalDataUpdate):
    db_additional_data = db.query(models.AdditionalData).filter(models.AdditionalData.id == additional_data_id).first()
    db_additional_data.repository = additional_data.repository
    db_additional_data.name = additional_data.name
    db_additional_data.full_name = additional_data.full_name
    db_additional_data.language = additional_data.language
    db_additional_data.forks_count = additional_data.forks_count
    db_additional_data.open_issues_count = additional_data.open_issues_count
    db_additional_data.created_at = additional_data.created_at
    db_additional_data.pushed_at = additional_data.pushed_at
    db_additional_data.updated_at = datetime.now()
    db.commit()
    db.refresh(db_additional_data)
    return db_additional_data

def delete_additional_data(db: Session, additional_data_id: str):
    db.query(models.AdditionalData).filter(models.AdditionalData.id == additional_data_id).delete()
    db.commit()
    return True

# pipeline
def get_pipeline_by_id(db: Session, pipeline_id: str):
    return db.query(models.Pipeline).filter(models.Pipeline.id == pipeline_id).first()

def get_pipelines(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Pipeline).order_by(models.Pipeline.created_at.desc()).offset(skip).limit(limit).all()

def get_pipelines_by_repository(db: Session, repository_id: str, skip: int = 0, limit: int = 100):
    return db.query(models.Pipeline).filter(models.Pipeline.repository == repository_id).order_by(models.Pipeline.created_at.desc()).offset(skip).limit(limit).all()

def create_pipeline(db: Session, pipeline: schemas.PipelineCreate):
    db_pipeline = models.Pipeline(**pipeline.dict())
    db.add(db_pipeline)
    db.commit()
    db.refresh(db_pipeline)
    return db_pipeline

def update_pipeline(db: Session, pipeline_id: str, pipeline: schemas.PipelineUpdate):
    db_pipeline = db.query(models.Pipeline).filter(models.Pipeline.id == pipeline_id).first()
    db_pipeline.repository = pipeline.repository
    db_pipeline.stage = pipeline.stage
    db_pipeline.created_at = pipeline.created_at
    db_pipeline.updated_at = datetime.now()
    db.commit()
    db.refresh(db_pipeline)
    return db_pipeline

def share_consent_pipeline(db: Session, pipeline_id: str, share_consent: bool):
    db_pipeline = db.query(models.Pipeline).filter(models.Pipeline.id == pipeline_id).first()
    db_pipeline.share_consent = share_consent
    db_pipeline.updated_at = datetime.now()
    db.commit()
    db.refresh(db_pipeline)
    return db_pipeline


def delete_pipeline(db: Session, pipeline_id: str):
    db.query(models.Pipeline).filter(models.Pipeline.id == pipeline_id).delete()
    db.commit()
    return True

#user
def get_user_by_id(db: Session, user_id: str):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_username_active(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username, models.User.status == UserStatusEnum.ACTIVE).first()

def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def user_exists(db: Session, username: str) -> bool:
    return db.query(models.User).filter(models.User.username == username).first() is not None

def create_user(db: Session, user: schemas.UserCreate):
    db_user = models.User()
    db_user.username = user.username
    db_user.hashed_password = hash_password(user.password)
    db_user.fullname = user.fullname
    db_user.email = user.email
    db_user.status = UserStatusEnum.ACTIVE
    db_user.created_at = datetime.now()

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user

def update_user(db: Session, user_id: str, user: schemas.UserUpdate):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    db_user.fullname = user.fullname
    db_user.email = user.email
    db_user.status = user.status
    db_user.created_at = user.created_at
    db_user.updated_at = datetime.now()
    db.commit()
    db.refresh(db_user)

    return db_user

def save_integration_user(db: Session, username: str, github_token: str):
    db_user = db.query(models.User).filter(models.User.username == username, models.User.github_user == True).first()

    if db_user is None:
        db_user = models.User()
        db_user.created_at = datetime.now()
        db.add(db_user)

    db_user.username = username
    db_user.hashed_password = hash_password(str(uuid.uuid4()))
    db_user.status = UserStatusEnum.ACTIVE
    db_user.updated_at = datetime.now()
    db_user.github_user = True
    db_user.github_token = github_token

    db.commit()
    db.refresh(db_user)

    return db_user

def get_user_by_token_active(db: Session, token: str):
    return db.query(models.User).filter(models.User.github_token == token, models.User.status == UserStatusEnum.ACTIVE, models.User.github_user == True).first()

# commit
def create_commit(db: Session, commit_data: dict):
    db_commit = Commit(**commit_data)
    db.add(db_commit)

    db.commit()
    db.refresh(db_commit)

    return db_commit

def get_commits_by_pipeline(db: Session, pipeline_id: str):
    return db.query(models.Commit).filter(models.Commit.pipeline_id == pipeline_id).order_by(models.Commit.created_at.asc()).all()

def exits_commits_by_pipeline(db: Session, pipeline_id: str):
    return db.query(models.Commit).filter(models.Commit.pipeline_id == pipeline_id).first() is not None

def get_commits_grouped_by_author(db: Session, pipeline_id: str):
    return (db.query(models.Commit.author_name, func.count(models.Commit.id).label("commit_count"))
            .filter(models.Commit.pipeline_id == pipeline_id)
            .group_by(models.Commit.author_name)
            .order_by(desc(func.count(models.Commit.id)))
            .all())

# competence
def create_competence(db: Session, competence_data: dict):
    db_competence = Competence(**competence_data)
    db.add(db_competence)

    db.commit()
    db.refresh(db_competence)

    return db_competence

def get_competences_by_pipeline(db: Session, pipeline_id: str):
    return db.query(models.Competence).filter(models.Competence.pipeline_id == pipeline_id).order_by(models.Competence.created_at.asc()).all()

def exits_competences_by_pipeline(db: Session, pipeline_id: str):
    return db.query(models.Competence).filter(models.Competence.pipeline_id == pipeline_id).first() is not None

# base_item
def create_base_item(db: Session, base_item_data: dict):
    db_base_item = BaseItem(**base_item_data)
    db.add(db_base_item)

    db.commit()
    db.refresh(db_base_item)

    return db_base_item

def get_base_items_by_pipeline(db: Session, pipeline_id: str):
    return db.query(models.BaseItem).filter(models.BaseItem.pipeline_id == pipeline_id).order_by(models.BaseItem.created_at.asc()).all()

def exits_base_items_by_pipeline(db: Session, pipeline_id: str):
    return db.query(models.BaseItem).filter(models.BaseItem.pipeline_id == pipeline_id).first() is not None

# test_data
def create_test_data(db: Session, test_data: dict):
    db_test_data = TestData(**test_data)
    db.add(db_test_data)

    db.commit()
    db.refresh(db_test_data)

    return db_test_data

def get_test_datas_by_pipeline(db: Session, pipeline_id: str):
    return db.query(models.TestData).filter(models.TestData.pipeline_id == pipeline_id).order_by(models.TestData.commit_order.asc(), models.TestData.created_at.asc()).all()

def exits_test_datas_by_pipeline(db: Session, pipeline_id: str):
    return db.query(models.TestData).filter(models.TestData.pipeline_id == pipeline_id).first() is not None

# code_metrics
def create_code_metrics(db: Session, code_metrics: dict):
    db_code_metrics = CodeMetrics(**code_metrics)
    db.add(db_code_metrics)

    db.commit()
    db.refresh(db_code_metrics)

    return db_code_metrics

def get_code_metrics_by_pipeline(db: Session, pipeline_id: str):
    return db.query(models.CodeMetrics).filter(models.CodeMetrics.pipeline_id == pipeline_id).order_by(models.CodeMetrics.created_at.asc()).all()

def exits_code_metrics_by_pipeline(db: Session, pipeline_id: str):
    return db.query(models.CodeMetrics).filter(models.CodeMetrics.pipeline_id == pipeline_id).first() is not None

# project_dimension
def create_project_dimension(db: Session, project_dimension: dict):
    db_project_dimension = ProjectDimension(**project_dimension)
    db.add(db_project_dimension)

    db.commit()
    db.refresh(db_project_dimension)

    return db_project_dimension

def get_project_dimension_by_pipeline(db: Session, pipeline_id: str):
    return db.query(models.ProjectDimension).filter(models.ProjectDimension.pipeline_id == pipeline_id).order_by(models.ProjectDimension.created_at.asc()).first()

def exits_project_dimension_by_pipeline(db: Session, pipeline_id: str):
    return db.query(models.ProjectDimension).filter(models.ProjectDimension.pipeline_id == pipeline_id).first() is not None

# commit_message_item
def create_commit_message_item(db: Session, commit_message_item: dict):
    db_commit_message_item = CommitMessageItem(**commit_message_item)
    db.add(db_commit_message_item)

    db.commit()
    db.refresh(db_commit_message_item)

    return db_commit_message_item

def get_commit_message_items_by_pipeline(db: Session, pipeline_id: str):
    return db.query(models.CommitMessageItem).filter(models.CommitMessageItem.pipeline_id == pipeline_id).order_by(models.CommitMessageItem.created_at.asc()).all()

def exits_commit_message_items_by_pipeline(db: Session, pipeline_id: str):
    return db.query(models.CommitMessageItem).filter(models.CommitMessageItem.pipeline_id == pipeline_id).first() is not None

# maintenance_activity_summary
def create_maintenance_activity_summary(db: Session, maintenance_activity_summary: dict):
    db_maintenance_activity_summary = MaintenanceActivitySummary(**maintenance_activity_summary)
    db.add(db_maintenance_activity_summary)

    db.commit()
    db.refresh(db_maintenance_activity_summary)

    return db_maintenance_activity_summary

def get_maintenance_activity_summary_by_pipeline(db: Session, pipeline_id: str):
    return db.query(models.MaintenanceActivitySummary).filter(models.MaintenanceActivitySummary.pipeline_id == pipeline_id).order_by(models.MaintenanceActivitySummary.created_at.asc()).first()

def exits_maintenance_activity_summary_by_pipeline(db: Session, pipeline_id: str):
    return db.query(models.MaintenanceActivitySummary).filter(models.MaintenanceActivitySummary.pipeline_id == pipeline_id).first() is not None

# correlation
def create_correlation(db: Session, correlation: dict):
    db_correlation = Correlation(**correlation)
    db.add(db_correlation)

    db.commit()
    db.refresh(db_correlation)

    return db_correlation

def get_correlation_by_pipeline(db: Session, pipeline_id: str):
    return db.query(models.Correlation).filter(models.Correlation.pipeline_id == pipeline_id).order_by(models.Correlation.created_at.asc()).first()

def exits_correlation_by_pipeline(db: Session, pipeline_id: str):
    return db.query(models.Correlation).filter(models.Correlation.pipeline_id == pipeline_id).first() is not None

# code_distribution_details
def create_code_detail(db: Session, detail_data: dict):
    db_detail_data = CodeDistributionDetail(**detail_data)
    db.add(db_detail_data)

    db.commit()
    db.refresh(db_detail_data)

    return db_detail_data

def get_code_distribution_details_by_pipeline_and_commit_order(db: Session, pipeline_id: str, commit_order: int):
    return (db.query(models.CodeDistributionDetail)
            .filter(models.CodeDistributionDetail.pipeline_id == pipeline_id,
                    models.CodeDistributionDetail.commit_order == commit_order)
            .order_by(models.CodeDistributionDetail.created_at.asc())
            .all())

# insights
def create_insights(db: Session, insights: dict):
    db_insights = Insights(**insights)
    db.add(db_insights)

    db.commit()
    db.refresh(db_insights)

    return db_insights

def get_insights_by_pipeline(db: Session, pipeline_id: str):
    return db.query(models.Insights).filter(models.Insights.pipeline_id == pipeline_id).order_by(models.Insights.created_at.asc()).first()

def exits_insights_by_pipeline(db: Session, pipeline_id: str):
    return db.query(models.Insights).filter(models.Insights.pipeline_id == pipeline_id).first() is not None

