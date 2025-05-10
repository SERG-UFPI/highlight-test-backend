from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydriller import Repository
from .. import schemas, crud
from ..constants import *
from ..database import get_db
from ..dtos.my_project_result import MyProjectResult
from ..enums import StatusEnum
from ..helpers.http_utils import start_process_safe
from ..schemas import StageEnum
from ..celery_config import celery_app
from app.helpers.utils import save_csv, save_json
from ..logger_config import *

router = APIRouter(
    prefix="/process/extract_commits",
    tags=["extract_commits"],
    responses={404: {"description": "Pipeline not found"}},
)

@router.post("/", status_code=status.HTTP_202_ACCEPTED)
async def extract_history(process: schemas.ProcessBase, db: Session = Depends(get_db)):
    db_pipeline = crud.get_pipeline_by_id(db, pipeline_id=process.pipeline_id)
    if db_pipeline is None:
        raise HTTPException(status_code=404, detail="Pipeline not found")

    db_pipeline.stage = StageEnum.EXTRACT_COMMITS
    db_pipeline.status = StatusEnum.IN_PROGRESS
    db_pipeline.updated_at = datetime.now()
    db.commit()
    db.refresh(db_pipeline)

    extract_history_task.delay(process.pipeline_id)

    return {}

@celery_app.task
def extract_history_task(pipeline_id: str):
    logger.info(f"{datetime.now()} : BEGIN extract_history_task pipeline_id {pipeline_id}")

    db = next(get_db())

    db_pipeline = crud.get_pipeline_by_id(db, pipeline_id=pipeline_id)
    if db_pipeline is None:
        raise HTTPException(status_code=404, detail="Pipeline not found")

    db_repository = crud.get_repository_by_id(db, repository_id=db_pipeline.repository)
    if db_repository is None:
        raise HTTPException(status_code=404, detail="Repository not found")

    clone_url = db_repository.clone_url

    try:
        db_additional_data = crud.get_additional_data_by_repository(db, repository_id=db_repository.id)
        if db_additional_data is None:
            raise HTTPException(status_code=404, detail="AdditionalData not found")

        project_result = MyProjectResult(db_additional_data, pipeline_id)

        path_git = os.path.join(BASE_PROJECTS, str(pipeline_id), project_result.base_git)

        if not os.path.exists(path_git):
            raise Exception(f"Path {path_git} does not exist")

        contents = ""
        for commit in Repository(path_git).traverse_commits():
            contents += f"{commit.hash};{commit.author.name};{commit.committer.name};{commit.author_date.strftime('%Y-%m-%d %H:%M:%S')};{commit.msg};\n"

        save_csv(BASE_LOG_COMMITS, str(project_result.id), contents)

        logger.info(f"{datetime.now()} : END extract_history_task pipeline_id {pipeline_id}")

        extract_revisions_task.delay(pipeline_id)

    except Exception as e:
        db_pipeline.status = StatusEnum.ERROR
        db_pipeline.updated_at = datetime.now()
        logger.error(f"Extract_history_task {clone_url} failed. Error: {e}")
        raise e

    finally:
        db.commit()
        db.refresh(db_pipeline)

@celery_app.task
def extract_revisions_task(pipeline_id: str):
    logger.info(f"{datetime.now()} : BEGIN extract_revisions_task pipeline_id {pipeline_id}")

    db = next(get_db())

    db_pipeline = crud.get_pipeline_by_id(db, pipeline_id=pipeline_id)
    if db_pipeline is None:
        raise HTTPException(status_code=404, detail="Pipeline not found")

    db_repository = crud.get_repository_by_id(db, repository_id=db_pipeline.repository)
    if db_repository is None:
        raise HTTPException(status_code=404, detail="Repository not found")

    try:
        db_additional_data = crud.get_additional_data_by_repository(db, repository_id=db_repository.id)
        if db_additional_data is None:
            raise HTTPException(status_code=404, detail="AdditionalData not found")

        project_result = MyProjectResult(db_additional_data, pipeline_id)

        csv_path = os.path.join(BASE_LOG_COMMITS, f"{project_result.id}.csv")
        if not os.path.exists(csv_path):
            raise Exception(f"CSV file {csv_path} does not exist")

        with open(csv_path, 'r', encoding='latin-1') as file:
            base = []
            competences = []
            for row in file:
                row_data = row.split(";")
                if len(row_data) > 5:
                    competence = row_data[3][0:7]
                    if competence not in competences:
                        competences.append(competence)
                        base.append(row_data[0])

        if base:
            save_json(BASE_LOG_PERIOD_REVISIONS, str(project_result.id), competences)
            save_json(BASE_LOG_REVISIONS, str(project_result.id), base)
        else:
            logger.error(f"{datetime.now()} : extract_revisions_task pipeline_id {pipeline_id} failed. No data found.")

        db_pipeline.status = StatusEnum.COMPLETED
        db_pipeline.updated_at = datetime.now()
        logger.info(f"{datetime.now()} : END extract_revisions_task pipeline_id {pipeline_id}")

        db.commit()
        db.refresh(db_pipeline)

        start_process_safe("generate_timeseries", pipeline_id)

    except Exception as e:
        db_pipeline.status = StatusEnum.ERROR
        db_pipeline.updated_at = datetime.now()
        logger.error(f"{datetime.now()} : extract_revisions_task pipeline_id {pipeline_id} failed. Error: {e}")

        db.commit()
        db.refresh(db_pipeline)

        raise e