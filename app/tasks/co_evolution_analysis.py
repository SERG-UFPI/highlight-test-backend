from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from scipy.stats import pearsonr
from .. import schemas, crud
from ..database import get_db
from ..dtos.my_project_result import MyProjectResult
from ..enums import StatusEnum
from ..helpers.co_evolution_utils import check_coevolution
from ..schemas import StageEnum
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

        code_metrics = crud.get_code_metrics_by_pipeline(db, project_result.id)

        production_metric = next((metric for metric in code_metrics if metric.metric_type == 'production'), None)

        test_metric = next((metric for metric in code_metrics if metric.metric_type == 'test'), None)

        if not production_metric:
            raise HTTPException(status_code=404, detail="No production metric found")

        if not test_metric:
            raise HTTPException(status_code=404, detail="No test metric found")

        pcc_val = float(check_coevolution(production_metric.timeseries, test_metric.timeseries))

        correlation = {
            "pearson_correlation": pcc_val,
            "pipeline_id": pipeline_id,
        }

        crud.create_correlation(db, correlation)

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

