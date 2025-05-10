import uuid

from sqlalchemy import and_, or_
from sqlalchemy.orm import Session

from . import models, schemas
from datetime import datetime

from .enums import UserStatusEnum
from .helpers.user_utils import hash_password


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

#pipeline
def get_pipeline_by_id(db: Session, pipeline_id: str):
    return db.query(models.Pipeline).filter(models.Pipeline.id == pipeline_id).first()

def get_pipelines(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Pipeline).order_by(models.Pipeline.created_at.desc()).offset(skip).limit(limit).all()

def get_pipelines_by_repository(db: Session, repository_id: str, skip: int = 0, limit: int = 100):
    return db.query(models.Pipeline).filter(models.Pipeline.repository == repository_id).offset(skip).limit(limit).all()

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


