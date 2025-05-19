from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from .. import schemas, crud
from ..constants import *
from ..database import get_db
from ..dtos.my_project_result import MyProjectResult
from app.libs.test_code_classification.fileAnalysis import test_include, test_keyword
from app.libs.test_code_classification.utilities import lookup_generator, tech_lookup_generator
from ..enums import StatusEnum
from ..helpers.generate_timeseries_utils import process_cloc_history, cloc_series
from ..helpers.http_utils import start_process_safe
from ..schemas import StageEnum
from ..celery_config import celery_app
from app.helpers.utils import clean_create_dir, is_windows
from ..logger_config import *

router = APIRouter(
    prefix="/process/generate_timeseries",
    tags=["generate_timeseries"],
    responses={404: {"description": "Pipeline not found"}},
)

@router.post("/", status_code=status.HTTP_202_ACCEPTED)
async def generate_timeseries(process: schemas.ProcessBase, db: Session = Depends(get_db)):
    db_pipeline = crud.get_pipeline_by_id(db, pipeline_id=process.pipeline_id)
    if db_pipeline is None:
        raise HTTPException(status_code=404, detail="Pipeline not found")

    db_pipeline.stage = StageEnum.GENERATE_TIME_SERIES
    db_pipeline.status = StatusEnum.IN_PROGRESS
    db_pipeline.updated_at = datetime.now()

    db.commit()
    db.refresh(db_pipeline)

    generate_timeseries_task.delay(process.pipeline_id)

    return {}

@celery_app.task
def generate_timeseries_task(pipeline_id: str):
    logger.info(f"{datetime.now()} : BEGIN generate_timeseries_task pipeline_id {pipeline_id}")

    keyword_lookup = lookup_generator(os.path.join(TEST_CODE_CLASSIFICATION_DIR, "keywords.txt"))
    tech_lookup = tech_lookup_generator(os.path.join(TEST_CODE_CLASSIFICATION_DIR, "testingTechnologiesFixed3.csv"))

    calculate_loc = True

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

        base_itens = crud.get_base_items_by_pipeline(db, project_result.id)
        commit_history = [revision.base_item for revision in base_itens]

        if not commit_history:
            return False

        commit_order = 0

        clean_create_dir(os.path.join(BASE_LOG_TEST_FILE, str(project_result.id)))

        if calculate_loc:
            clean_create_dir(os.path.join(BASE_LOG_LOC, str(project_result.id)))

        for commit_hash in commit_history:
            if commit_hash == "":
                commit_order += 1
                continue

            base_git_path = os.path.join(BASE_PROJECTS, str(pipeline_id), project_result.base_git)

            if is_windows():
                command = f"cd {base_git_path} && git checkout -f {commit_hash} && git stash --all"
            else:
                command = f"cd {base_git_path} && git checkout -f {commit_hash} && git stash --all && chmod -R 777 {base_git_path}"

            os.system(command)

            test_path_log = os.path.join(BASE_LOG_TEST_FILE, str(project_result.id), str(commit_order))

            if calculate_loc:
                loc_path_log = os.path.join(BASE_LOG_LOC, str(project_result.id), str(commit_order))

            clean_create_dir(test_path_log)
            if calculate_loc:
                clean_create_dir(loc_path_log)

            for path_item, _, files_git_path in os.walk(base_git_path):
                for file_git_path in files_git_path:
                    try:
                        file_extension = file_git_path.rpartition(".")[-1]
                        if file_extension in FILE_EXTENSION_ACCEPTED:

                            file_contents = ""
                            file = os.path.join(base_git_path, path_item, file_git_path)

                            with open(file, "r", encoding="latin-1") as opened_file:
                                for line in opened_file:
                                    file_contents += line + "\n"

                            file_contents += " " + file_contents

                            has_test_import = test_include(tech_lookup, file_extension, file_contents)
                            has_test_call = test_keyword(keyword_lookup, file_extension, file_contents)

                            is_test_file = 0
                            if has_test_import + has_test_call == 2:
                                is_test_file = 1

                            db_test_data = {
                                "file_path": file,
                                "is_test_file": is_test_file,
                                "has_test_import": has_test_import,
                                "has_test_call": has_test_call,
                                "pipeline_id": pipeline_id,
                                "commit_order": commit_order
                            }

                            crud.create_test_data(db, db_test_data)

                    except Exception as e:
                        logger.error(f"Error processing file {file_git_path}: {e}")
                        continue

            if calculate_loc:
                process_cloc_history(base_git_path, loc_path_log)

            commit_order += 1

        logger.info(f"{datetime.now()} : END generate_timeseries_task pipeline_id {pipeline_id}")

        cloc_series_history_task.delay(pipeline_id)

    except Exception as e:
        db_pipeline.status = StatusEnum.ERROR
        db_pipeline.updated_at = datetime.now()
        logger.error(f"{datetime.now()} : generate_timeseries_task pipeline_id {pipeline_id} failed. Error: {e}")
        raise e

    finally:
        db.commit()
        db.refresh(db_pipeline)

@celery_app.task
def cloc_series_history_task(pipeline_id: str):
    logger.info(f"{datetime.now()} : BEGIN cloc_series_history_task pipeline_id {pipeline_id}")

    classify_test_based_on_function = False

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

        data_series = cloc_series(pipeline_id, classify_test_based_on_function, db, db_additional_data.uses_external_id)

        ploc_entry = {
            "full_name": project_result.base_git,
            "timeseries": data_series[0],
            "metric_type": "production",
            "pipeline_id": pipeline_id
        }

        tloc_entry = {
            "full_name": project_result.base_git,
            "timeseries": data_series[1],
            "metric_type": "test",
            "pipeline_id": pipeline_id
        }

        crud.create_code_metrics(db, ploc_entry)
        crud.create_code_metrics(db, tloc_entry)

        db_pipeline.status = StatusEnum.COMPLETED
        db_pipeline.updated_at = datetime.now()

        logger.info(f"{datetime.now()} : END cloc_series_history_task pipeline_id {pipeline_id}")

        db.commit()
        db.refresh(db_pipeline)

        start_process_safe("calculate_metrics", pipeline_id)

    except Exception as e:
        db_pipeline.status = StatusEnum.ERROR
        db_pipeline.updated_at = datetime.now()
        logger.error(f"{datetime.now()} : cloc_series_history_task pipeline_id {pipeline_id} failed. Error: {e}")
        db.commit()
        db.refresh(db_pipeline)
        raise e