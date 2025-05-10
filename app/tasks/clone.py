from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from .. import schemas, crud
from ..database import get_db
from ..enums import StatusEnum
from ..helpers.http_utils import start_process_safe
from ..helpers.utils import is_empty
from ..schemas import StageEnum
from ..celery_config import celery_app
from ..constants import *
from ..logger_config import *

router = APIRouter(
    prefix="/process/clone",
    tags=["clone"],
    responses={404: {"description": "Pipeline not found"}},
)

@router.post("/", status_code=status.HTTP_202_ACCEPTED)
async def clone(process: schemas.ProcessBase, db: Session = Depends(get_db)):
    db_pipeline = crud.get_pipeline_by_id(db, pipeline_id=process.pipeline_id)
    if db_pipeline is None:
        raise HTTPException(status_code=404, detail="Pipeline not found")

    db_pipeline.stage = StageEnum.CLONE
    db_pipeline.status = StatusEnum.IN_PROGRESS
    db_pipeline.updated_at = datetime.now()
    db.commit()
    db.refresh(db_pipeline)

    clone_task.delay(process.pipeline_id)

    return {}

@celery_app.task
def clone_task(pipeline_id: str):
    logger.info(f"{datetime.now()} : BEGIN clone_task pipeline_id {pipeline_id}")

    db = next(get_db())

    db_pipeline = crud.get_pipeline_by_id(db, pipeline_id=pipeline_id)
    if db_pipeline is None:
        raise HTTPException(status_code=404, detail="Pipeline not found")

    db_repository = crud.get_repository_by_id(db, repository_id=db_pipeline.repository)
    if db_repository is None:
        raise HTTPException(status_code=404, detail="Repository not found")

    cloneurl = db_repository.clone_url

    try:
        db_additional_data = crud.get_additional_data_by_repository(db, repository_id=db_repository.id)
        if db_additional_data is None:
            raise HTTPException(status_code=404, detail="AdditionalData not found")

        fullname = db_additional_data.full_name
        create_directories(BASE_PROJECTS, str(pipeline_id))
        create_directories(BASE_PROJECTS + "/" + str(pipeline_id)+ "/", fullname)

        path_project = BASE_PROJECTS + "/" + str(pipeline_id) + "/" + fullname
        logger.info(f"Cloning in {path_project}")

        command = f"git clone --branch {db_repository.default_branch} {cloneurl} {path_project}"
        os.system(command)

        if is_empty(path_project):
            raise Exception(f"{path_project} is empty")

        db_pipeline.status = StatusEnum.COMPLETED
        db_pipeline.updated_at = datetime.now()
        logger.info(f"{datetime.now()} : END clone_task pipeline_id {pipeline_id}")

        db.commit()
        db.refresh(db_pipeline)

        start_process_safe("extract_commits", pipeline_id)

    except Exception as e:
        db_pipeline.status = StatusEnum.ERROR
        db_pipeline.updated_at = datetime.now()
        logger.error(f"{datetime.now()} : clone_task pipeline_id {pipeline_id} failed. Error: {e}")

        db.commit()
        db.refresh(db_pipeline)

        raise e

def create_directories(path_projects: str, fullname: str):
    mode = 0o0777
    data = fullname.split('/')
    created = []

    for item in data:
        created.append(item)
        path_to_file = "/".join(created)
        path_project = path_projects + path_to_file

        if not os.path.exists(path_project):
            os.mkdir(path_project, mode)