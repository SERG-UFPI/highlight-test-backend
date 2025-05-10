from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from scipy.stats import pearsonr
from .. import schemas, crud
from ..constants import *
from ..database import get_db
from ..dtos.my_project_result import MyProjectResult
from ..enums import StatusEnum
from ..schemas import StageEnum
from app.helpers.utils import get_json, save_json
from ..logger_config import *
import warnings

router = APIRouter(
    prefix="/process/co_evolution_analysis",
    tags=["co_evolution_analysis"],
    responses={404: {"description": "Pipeline not found"}},
)

@router.post("/", status_code=status.HTTP_202_ACCEPTED)
def co_evolution_analysis(process: schemas.ProcessBase, db: Session = Depends(get_db)):
    db_pipeline = crud.get_pipeline_by_id(db, pipeline_id=process.pipeline_id)
    if db_pipeline is None:
        raise HTTPException(status_code=404, detail="Pipeline not found")

    db_pipeline.stage = StageEnum.CO_EVOLUTION_ANALYSIS
    db_pipeline.status = StatusEnum.IN_PROGRESS
    db_pipeline.updated_at = datetime.now()
    db.commit()
    db.refresh(db_pipeline)

    pipeline_id = process.pipeline_id
    logger.info(f"{datetime.now()} : BEGIN co_evolution_analysis pipeline_id {pipeline_id}")

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

        production_code_list = get_json(os.path.join(BASE_LOG_CLOC, f"{project_result.id}_production_code_list.json"))

        if not production_code_list or 'timeseries' not in production_code_list[0]:
            raise HTTPException(status_code=404, detail="Production code list or timeseries not found")

        test_code_list = get_json(os.path.join(BASE_LOG_CLOC, f"{project_result.id}_test_code_list.json"))

        if not test_code_list or 'timeseries' not in test_code_list[0]:
            raise HTTPException(status_code=404, detail="Test code list or timeseries not found")

        pcc_val = check_coevolution(production_code_list[0]['timeseries'], test_code_list[0]['timeseries'])

        save_json(BASE_LOG_CO_EVOLUTION, str(project_result.id), {"pearson_correlation": pcc_val})

        logger.info(f"{datetime.now()} : END co_evolution_analysis pipeline_id {pipeline_id}")

        db_pipeline.status = StatusEnum.COMPLETED
        db_pipeline.updated_at = datetime.now()

    except Exception as e:
        db_pipeline.status = StatusEnum.ERROR
        db_pipeline.updated_at = datetime.now()
        logger.error(f"{datetime.now()} : co_evolution_analysis pipeline_id {pipeline_id} failed. Error: {e}")
        raise e

    finally:
        db.commit()
        db.refresh(db_pipeline)

    return {"pearson_correlation": pcc_val}

def check_coevolution(series1, series2):
    try:
        with warnings.catch_warnings():
            warnings.filterwarnings("error", category=RuntimeWarning)
            return pearsonr(series1, series2)[0]
    except ValueError as e:
        print(f"ValueError: {e}")
        return -1
    except RuntimeWarning as e:
        print(f"RuntimeWarning: {e}")
        return -1
    except Exception as e:
        print(f"Unexpected error: {e}")
        return -1