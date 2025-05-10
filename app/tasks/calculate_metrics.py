from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from .. import schemas, crud
from ..constants import *
from ..database import get_db
from ..dtos.commit_maintenance_activities_result import CommitMaintenanceActivitiesResult
from ..dtos.my_project_result import MyProjectResult
from ..enums import StatusEnum
from ..helpers.calculate_metrics_utils import (
    get_project_dimension_repo, corrective_classifier, adaptive_classifier,
    adaptive_by_negation_classifier, perfective_classifier, refactor_classifier,
    save_maintenance_activities_log, get_maintenance_activities_repo
)
from ..helpers.http_utils import start_process_safe
from ..schemas import StageEnum
from ..celery_config import celery_app
from app.helpers.utils import save_json
from ..logger_config import *

router = APIRouter(
    prefix="/process/calculate_metrics",
    tags=["calculate_metrics"],
    responses={404: {"description": "Pipeline not found"}},
)

@router.post("/", status_code=status.HTTP_202_ACCEPTED)
async def calculate_metrics(process: schemas.ProcessBase, db: Session = Depends(get_db)):
    db_pipeline = crud.get_pipeline_by_id(db, pipeline_id=process.pipeline_id)
    if db_pipeline is None:
        raise HTTPException(status_code=404, detail="Pipeline not found")

    db_pipeline.stage = StageEnum.CALCULATE_METRICS
    db_pipeline.status = StatusEnum.IN_PROGRESS
    db_pipeline.updated_at = datetime.now()

    db.commit()
    db.refresh(db_pipeline)

    project_dimension_task.delay(process.pipeline_id)

    return {}

@celery_app.task
def project_dimension_task(pipeline_id: str):
    logger.info(f"{datetime.now()} : BEGIN project_dimension_task pipeline_id {pipeline_id}")

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

        data_repo = get_project_dimension_repo(project_result)
        n_commits = data_repo["n_commits"]
        n_devs = data_repo["n_authors"]

        n_forks_count = project_result.forks_count
        n_open_issues_count = project_result.open_issues_count

        save_json(BASE_LOG_PROJECT_DIMENSION, str(project_result.id), {
            "n_commits": n_commits, "n_devs": n_devs, "n_forks_count": n_forks_count, "n_open_issues_count": n_open_issues_count
        })

        commit_classification_task.delay(pipeline_id)

        logger.info(f"{datetime.now()} : END project_dimension_task pipeline_id {pipeline_id}")

    except Exception as e:
        db_pipeline.status = StatusEnum.ERROR
        db_pipeline.updated_at = datetime.now()
        logger.error(f"{datetime.now()} : project_dimension_task pipeline_id {pipeline_id} failed. Error: {e}")

        raise e

    finally:
        db.commit()
        db.refresh(db_pipeline)

@celery_app.task
def commit_classification_task(pipeline_id: str):
    logger.info(f"{datetime.now()} : BEGIN commit_classification_task pipeline_id {pipeline_id}")

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

        file_name = str(project_result.id) + ".csv"
        with open(os.path.join(BASE_LOG_COMMITS, file_name), "r", encoding="latin-1") as opened_file:
            commit_messages = {}

            file_content = opened_file.read()
            content_data = file_content.split(";\n")
            for line in content_data:
                data_line = line.split(';')
                if line == "\n\n" or len(data_line) < 5:
                    continue

                message = data_line[4].replace('\n', ' ')
                commit_messages[data_line[0]] = CommitMaintenanceActivitiesResult()
                commit_messages[data_line[0]].id = data_line[0]
                commit_messages[data_line[0]].message = message

        log_content = []
        for commit_message_key in commit_messages:
            commit_message_item = commit_messages[commit_message_key]
            commit_message_item.message = commit_message_item.message.lower()
            commit_message_item = corrective_classifier(commit_message_item)
            commit_message_item = adaptive_classifier(commit_message_item)
            commit_message_item = adaptive_by_negation_classifier(commit_message_item)
            commit_message_item = perfective_classifier(commit_message_item)
            commit_message_item = refactor_classifier(commit_message_item)

            log_content.append(commit_message_item)

        save_maintenance_activities_log(file_name, log_content)

        maintenance_activities_task.delay(pipeline_id)

        logger.info(f"{datetime.now()} : END commit_classification_task pipeline_id {pipeline_id}")

    except Exception as e:
        db_pipeline.status = StatusEnum.ERROR
        db_pipeline.updated_at = datetime.now()
        logger.error(f"{datetime.now()} : commit_classification_task pipeline_id {pipeline_id} failed. Error: {e}")

        raise e

    finally:
        db.commit()
        db.refresh(db_pipeline)

@celery_app.task
def maintenance_activities_task(pipeline_id: str):
    logger.info(f"{datetime.now()} : BEGIN maintenance_activities_task pipeline_id {pipeline_id}")

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

        data_repo = get_maintenance_activities_repo(project_result)

        result_repo_test_sum = data_repo["n_corrective"] + data_repo["n_adaptive"] + data_repo["n_perfective"]

        n_corrective = data_repo["n_corrective"] * 100 / result_repo_test_sum
        n_adaptive = data_repo["n_adaptive"] * 100 / result_repo_test_sum
        n_perfective = data_repo["n_perfective"] * 100 / result_repo_test_sum
        n_multi = data_repo["n_multi"] * 100 / result_repo_test_sum

        save_json(BASE_SUMMARY_MAINTENANCE_ACTIVITIES, str(project_result.id), {
            "n_corrective": n_corrective, "n_adaptive": n_adaptive, "n_perfective": n_perfective, "n_multi": n_multi
        })

        db_pipeline.status = StatusEnum.COMPLETED
        db_pipeline.updated_at = datetime.now()
        logger.info(f"{datetime.now()} : END maintenance_activities_task pipeline_id {pipeline_id}")

        db.commit()
        db.refresh(db_pipeline)

        start_process_safe("co_evolution_analysis", pipeline_id)

    except Exception as e:
        db_pipeline.status = StatusEnum.ERROR
        db_pipeline.updated_at = datetime.now()
        logger.error(f"{datetime.now()} : maintenance_activities_task pipeline_id {pipeline_id} failed. Error: {e}")

        db.commit()
        db.refresh(db_pipeline)

        raise e