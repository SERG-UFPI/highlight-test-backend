from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import schemas, crud
from app.constants import *
from app.database import get_db
from app.dtos.my_project_result import MyProjectResult
from app.enums import LanguageEnum
from app.helpers.utils import get_json, div_safe, get_comma_separated_names, parse_int, get_index
from app.helpers.calculate_metrics_utils import get_devs_group_by_commits, get_commits, get_maintenance_activities_details
from app.helpers.cluster_utils import get_cluster, CENTROIDS, CENTROIDS_NAME, CENTROIDS_DESCRIPTION
from app.helpers.co_evolution_utils import get_status_evolution, get_code_co_evolution, \
    preprocess_java_test_files, match_java_test_file_optimized
from app.helpers.generate_timeseries_utils import get_files
from app.helpers.generated_text_utils import generate_cluster_insights
from app.logger_config import *

router = APIRouter(
    prefix="/dashboards/general",
    tags=["general"],
    responses={404: {"description": "Pipeline not found"}},
)

@router.post("/commits")
def commits(process: schemas.ProcessBase, db: Session = Depends(get_db)):
    db_pipeline = crud.get_pipeline_by_id(db, pipeline_id=process.pipeline_id)
    if db_pipeline is None:
        raise HTTPException(status_code=404, detail="Pipeline not found")

    pipeline_id = process.pipeline_id
    logger.info(f"{datetime.now()} : BEGIN commits pipeline_id {pipeline_id}")

    db = next(get_db())

    db_pipeline = crud.get_pipeline_by_id(db, pipeline_id=pipeline_id)
    if db_pipeline is None:
        raise HTTPException(status_code=404, detail="Pipeline not found")

    db_repository = crud.get_repository_by_id(db, repository_id=db_pipeline.repository)
    if db_repository is None:
        raise HTTPException(status_code=404, detail="Repository not found")

    commits = []
    try:
        db_additional_data = crud.get_additional_data_by_repository(db, repository_id=db_repository.id)
        if db_additional_data is None:
            raise HTTPException(status_code=404, detail="AdditionalData not found")

        project_result = MyProjectResult(db_additional_data, pipeline_id)

        commits = get_commits(project_result)

    except Exception as e:

        logger.error(f"{datetime.now()} : commits pipeline_id {pipeline_id} failed. Error: {e}")
        raise e

    return {"commits": commits}

@router.post("/developers")
def developers(process: schemas.ProcessBase, db: Session = Depends(get_db)):
    db_pipeline = crud.get_pipeline_by_id(db, pipeline_id=process.pipeline_id)
    if db_pipeline is None:
        raise HTTPException(status_code=404, detail="Pipeline not found")

    pipeline_id = process.pipeline_id
    logger.info(f"{datetime.now()} : BEGIN developers pipeline_id {pipeline_id}")

    db = next(get_db())

    db_pipeline = crud.get_pipeline_by_id(db, pipeline_id=pipeline_id)
    if db_pipeline is None:
        raise HTTPException(status_code=404, detail="Pipeline not found")

    db_repository = crud.get_repository_by_id(db, repository_id=db_pipeline.repository)
    if db_repository is None:
        raise HTTPException(status_code=404, detail="Repository not found")

    developers = []
    try:
        db_additional_data = crud.get_additional_data_by_repository(db, repository_id=db_repository.id)
        if db_additional_data is None:
            raise HTTPException(status_code=404, detail="AdditionalData not found")

        project_result = MyProjectResult(db_additional_data, pipeline_id)

        developers = get_devs_group_by_commits(project_result)

        if developers and len(developers) > 0:
            developers.sort(key=lambda x: x["commits"], reverse=True)

    except Exception as e:

        logger.error(f"{datetime.now()} : developers pipeline_id {pipeline_id} failed. Error: {e}")
        raise e

    return {"developers": developers}

@router.post("/code_distribution")
def code_distribution(process: schemas.ProcessBase, db: Session = Depends(get_db)):
    db_pipeline = crud.get_pipeline_by_id(db, pipeline_id=process.pipeline_id)
    if db_pipeline is None:
        raise HTTPException(status_code=404, detail="Pipeline not found")

    pipeline_id = process.pipeline_id
    logger.info(f"{datetime.now()} : BEGIN code_distribution pipeline_id {pipeline_id}")

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

        total_code = production_code_list[0]['timeseries'][-1] + test_code_list[0]['timeseries'][-1]
        production_code = f"{div_safe(production_code_list[0]['timeseries'][-1] * 100, total_code):.2f}"
        test_code = f"{div_safe(test_code_list[0]['timeseries'][-1] * 100, total_code):.2f}"

        logger.info(f"{datetime.now()} : END code_distribution pipeline_id {pipeline_id}")

    except Exception as e:

        logger.error(f"{datetime.now()} : code_distribution pipeline_id {pipeline_id} failed. Error: {e}")
        raise e

    return {"production_code": production_code, "test_code": test_code}


@router.post("/code_distribution_details")
def code_distribution_details(process: schemas.ProcessBase, db: Session = Depends(get_db)):
    db_pipeline = crud.get_pipeline_by_id(db, pipeline_id=process.pipeline_id)
    if db_pipeline is None:
        raise HTTPException(status_code=404, detail="Pipeline not found")

    pipeline_id = process.pipeline_id
    logger.info(f"{datetime.now()} : BEGIN code_distribution_details pipeline_id {pipeline_id}")

    db = next(get_db())

    db_pipeline = crud.get_pipeline_by_id(db, pipeline_id=pipeline_id)
    if db_pipeline is None:
        raise HTTPException(status_code=404, detail="Pipeline not found")

    db_repository = crud.get_repository_by_id(db, repository_id=db_pipeline.repository)
    if db_repository is None:
        raise HTTPException(status_code=404, detail="Repository not found")

    contents = []
    try:
        db_additional_data = crud.get_additional_data_by_repository(db, repository_id=db_repository.id)
        if db_additional_data is None:
            raise HTTPException(status_code=404, detail="AdditionalData not found")

        project_result = MyProjectResult(db_additional_data, pipeline_id)

        revisions = get_json(os.path.join(BASE_LOG_PERIOD_REVISIONS, str(project_result.id) + '.json'))
        revision_length = len(revisions)

        commit_order = revision_length-1

        files_data = get_files(str(project_result.id), commit_order, False)

        p_files = files_data["p_files"]
        t_files = files_data["t_files"]

        valid_cloc = False
        opened_file = open(os.path.join(BASE_LOG_LOC, str(project_result.id), str(commit_order), 'cloc.log'), "r",
                           encoding="latin-1")

        for line in opened_file:

            if (db_additional_data.uses_external_id and line.find(IMPORTED_PROJECTS_FOLDER_NAME) == -1) or \
                    (not db_additional_data.uses_external_id and line.find(BASE_PROJECTS_FOLDER_NAME) == -1):
                continue

            if not valid_cloc:
                valid_cloc = True

            # language;filename;blank;comment;code;
            line_data = line.split(',')

            path_query = get_comma_separated_names(line_data, 5, 1, 2).replace('\\', '/').replace('//', '/')

            if db_additional_data.uses_external_id:
                simple_name_path = path_query.rpartition(IMPORTED_PROJECTS_FOLDER_NAME + "/")[-1]
            else:
                simple_name_path = path_query.rpartition(str(project_result.id) + "/")[-1]

            value = parse_int(line_data[-1].replace('\n', ''))

            extension = path_query.rpartition(".")[-1]
            if extension not in FILE_EXTENSION_ACCEPTED:
                continue

            if path_query in p_files:
                contents.append({"path": simple_name_path, "loc": value, "is_test_file": False})
                continue

            if path_query in t_files:
                contents.append({"path": simple_name_path, "loc": value, "is_test_file": True})
                continue


        logger.info(f"{datetime.now()} : END code_distribution_details pipeline_id {pipeline_id}")

    except Exception as e:

        logger.error(f"{datetime.now()} : code_distribution_details pipeline_id {pipeline_id} failed. Error: {e}")
        raise e

    if contents and len(contents) > 0:
        contents.sort(key=lambda x: x["loc"], reverse=True)

    return {"contents": contents}


@router.post("/co_evolution")
def co_evolution(process: schemas.ProcessBase, db: Session = Depends(get_db)):
    db_pipeline = crud.get_pipeline_by_id(db, pipeline_id=process.pipeline_id)
    if db_pipeline is None:
        raise HTTPException(status_code=404, detail="Pipeline not found")

    pipeline_id = process.pipeline_id
    logger.info(f"{datetime.now()} : BEGIN co_evolution pipeline_id {pipeline_id}")

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

        revisions = get_json(os.path.join(BASE_LOG_PERIOD_REVISIONS, str(project_result.id) + '.json'))

        production_code_list = get_json(os.path.join(BASE_LOG_CLOC, f"{project_result.id}_production_code_list.json"))

        if not production_code_list or 'timeseries' not in production_code_list[0]:
            raise HTTPException(status_code=404, detail="Production code list or timeseries not found")

        test_code_list = get_json(os.path.join(BASE_LOG_CLOC, f"{project_result.id}_test_code_list.json"))

        if not test_code_list or 'timeseries' not in test_code_list[0]:
            raise HTTPException(status_code=404, detail="Test code list or timeseries not found")

        ratio_code_list = []
        ratio_production_code_list = []
        ratio_test_code_list = []
        i = 0

        production_code_max = max(production_code_list[0]['timeseries'])
        test_code_max = max(test_code_list[0]['timeseries'])

        for test_code in test_code_list[0]['timeseries']:
            production_code = production_code_list[0]['timeseries'][i]

            total_code = production_code + test_code
            ratio = f"{div_safe(test_code * 100, total_code):.2f}"
            ratio_production_code = f"{div_safe(production_code * 100, production_code_max):.2f}"
            ratio_test_code = f"{div_safe(test_code * 100, test_code_max):.2f}"

            ratio_code_list.append(ratio)
            ratio_production_code_list.append(ratio_production_code)
            ratio_test_code_list.append(ratio_test_code)

            i = i + 1

        logger.info(f"{datetime.now()} : END co_evolution pipeline_id {pipeline_id}")

    except Exception as e:

        logger.error(f"{datetime.now()} : co_evolution pipeline_id {pipeline_id} failed. Error: {e}")
        raise e

    return {"revisions": revisions, "production_code": ratio_production_code_list, "test_code": ratio_test_code_list, "ratio_code": ratio_code_list}


@router.post("/co_evolution_details")
def co_evolution_details(process: schemas.ProcessRevision, db: Session = Depends(get_db)):
    db_pipeline = crud.get_pipeline_by_id(db, pipeline_id=process.pipeline_id)
    if db_pipeline is None:
        raise HTTPException(status_code=404, detail="Pipeline not found")

    pipeline_id = process.pipeline_id
    logger.info(f"{datetime.now()} : BEGIN co_evolution_details pipeline_id {pipeline_id}")

    db = next(get_db())

    db_pipeline = crud.get_pipeline_by_id(db, pipeline_id=pipeline_id)
    if db_pipeline is None:
        raise HTTPException(status_code=404, detail="Pipeline not found")

    db_repository = crud.get_repository_by_id(db, repository_id=db_pipeline.repository)
    if db_repository is None:
        raise HTTPException(status_code=404, detail="Repository not found")

    contents = []
    try:
        db_additional_data = crud.get_additional_data_by_repository(db, repository_id=db_repository.id)
        if db_additional_data is None:
            raise HTTPException(status_code=404, detail="AdditionalData not found")

        project_result = MyProjectResult(db_additional_data, pipeline_id)

        if project_result.project_language != LanguageEnum.JAVA:
            raise HTTPException(status_code=415, detail="This resource is only implemented for Java projects.")

        revisions = get_json(os.path.join(BASE_LOG_PERIOD_REVISIONS, str(project_result.id) + '.json'))

        revision_index = get_index(revisions, process.revision)

        if revision_index == -1:
            raise HTTPException(status_code=404, detail="Revision not found")

        previous_revision_index = revision_index - 1
        if previous_revision_index == -1:
            commits_range = [revision_index]
        else:
            commits_range = [previous_revision_index, revision_index]

        previous_p_files_list = []
        previous_t_files_list = []

        for commit_order in commits_range:

            p_files_list = []
            t_files_list = []

            files_data = get_files(str(project_result.id), commit_order, False)

            p_files = files_data["p_files"]
            t_files = files_data["t_files"]

            valid_cloc = False
            opened_file = open(os.path.join(BASE_LOG_LOC, str(project_result.id), str(commit_order), 'cloc.log'), "r",
                               encoding="latin-1")

            for line in opened_file:

                if (db_additional_data.uses_external_id and line.find(IMPORTED_PROJECTS_FOLDER_NAME) == -1) or \
                        (not db_additional_data.uses_external_id and line.find(BASE_PROJECTS_FOLDER_NAME) == -1):
                    continue

                if not valid_cloc:
                    valid_cloc = True

                # language;filename;blank;comment;code;
                line_data = line.split(',')

                language = line_data[0]

                path_query = get_comma_separated_names(line_data, 5, 1, 2).replace('\\', '/').replace('//', '/')

                if db_additional_data.uses_external_id:
                    simple_name_path = path_query.rpartition(IMPORTED_PROJECTS_FOLDER_NAME+"/")[-1]
                else:
                    simple_name_path = path_query.rpartition(str(project_result.id) + "/")[-1]

                value = parse_int(line_data[-1].replace('\n', ''))

                extension = path_query.rpartition(".")[-1]
                if extension not in FILE_EXTENSION_ACCEPTED:
                    continue

                if path_query in p_files:
                    p_files_list.append({"path": simple_name_path, "loc": value, "is_test_file": False, "language": language})
                    continue

                if path_query in t_files:
                    t_files_list.append({"path": simple_name_path, "loc": value, "is_test_file": True, "language": language})
                    continue

            test_files_map = preprocess_java_test_files(t_files_list)

            for p_file_item in p_files_list:
                if p_file_item['language'] == "Java":
                    t_file_item = match_java_test_file_optimized(p_file_item, test_files_map)
                else:
                    t_file_item = {}

                p_status_evolution = get_status_evolution(p_file_item, previous_p_files_list)
                t_status_evolution = get_status_evolution(t_file_item, previous_t_files_list)
                code_co_evolution = get_code_co_evolution(p_status_evolution, t_status_evolution)

                if t_file_item:
                    file_item = {
                        "p_path": p_file_item["path"],
                        "p_loc": p_file_item["loc"],
                        "p_status_evolution": p_status_evolution,
                        "t_path": t_file_item["path"],
                        "t_loc": t_file_item["loc"],
                        "t_status_evolution": t_status_evolution,
                        "code_co_evolution": code_co_evolution,
                        "revision": revisions[commit_order]
                    }

                    if commit_order != previous_revision_index and file_item["p_status_evolution"] != 'Clean':
                        contents.append(file_item)

            previous_p_files_list = p_files_list
            previous_t_files_list = t_files_list

        logger.info(f"{datetime.now()} : END co_evolution_details pipeline_id {pipeline_id}")

    except Exception as e:

        logger.error(f"{datetime.now()} : co_evolution_details pipeline_id {pipeline_id} failed. Error: {e}")
        raise e

    if contents and len(contents) > 0:
        contents.sort(key=lambda x: (x["revision"], x["p_path"]), reverse=False)

    return {"contents": contents}


@router.post("/clustering")
def clustering(process: schemas.ProcessBase, db: Session = Depends(get_db)):
    db_pipeline = crud.get_pipeline_by_id(db, pipeline_id=process.pipeline_id)
    if db_pipeline is None:
        raise HTTPException(status_code=404, detail="Pipeline not found")

    pipeline_id = process.pipeline_id
    logger.info(f"{datetime.now()} : BEGIN clustering pipeline_id {pipeline_id}")

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

        ratio_code_list = []
        i = 0
        for test_code in test_code_list[0]['timeseries']:
            production_code = production_code_list[0]['timeseries'][i]

            total_code = production_code + test_code
            ratio = f"{div_safe(test_code * 100, total_code):.2f}"

            ratio_code_list.append(ratio)

            i = i + 1

        index = get_cluster(ratio_code_list, CENTROIDS)
        if index is None:
            raise HTTPException(status_code=404, detail="Cluster not found")

        cluster_name = CENTROIDS_NAME[index]
        cluster_description = CENTROIDS_DESCRIPTION[index]
        cluster_timeseries = CENTROIDS[index]

        cluster_insights = get_insights(project_result.id, ratio_code_list, cluster_name, cluster_timeseries, cluster_description)

        logger.info(f"{datetime.now()} : END clustering pipeline_id {pipeline_id}")

    except Exception as e:

        logger.error(f"{datetime.now()} : clustering pipeline_id {pipeline_id} failed. Error: {e}")
        raise e

    return {"cluster_name": cluster_name, "cluster_insights": cluster_insights}

def get_insights(project_id, repo_timeseries, cluster_name, cluster_timeseries, cluster_description):
    cluster_insights = get_json(os.path.join(BASE_LOG_CLOC, f"{project_id}_cluster_insights.json"))

    if cluster_insights :
        return cluster_insights["generated_text"]

    return generate_cluster_insights(project_id, repo_timeseries, cluster_name, cluster_timeseries, cluster_description)

@router.post("/correlation")
def correlation(process: schemas.ProcessBase, db: Session = Depends(get_db)):
    db_pipeline = crud.get_pipeline_by_id(db, pipeline_id=process.pipeline_id)
    if db_pipeline is None:
        raise HTTPException(status_code=404, detail="Pipeline not found")

    pipeline_id = process.pipeline_id
    logger.info(f"{datetime.now()} : BEGIN correlation pipeline_id {pipeline_id}")

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
        data = get_json(os.path.join(BASE_LOG_CO_EVOLUTION, f"{project_result.id}.json"))
        co_evolution_level = ""

        if data["pearson_correlation"] <= 0.5109762319120981:
            co_evolution_level = "Low Co-evolution"

        if data["pearson_correlation"] > 0.5109762319120981 and data["pearson_correlation"] <= 0.9614803284052508:
            co_evolution_level = "Moderate Co-evolution"

        if data["pearson_correlation"] > 0.9614803284052508:
            co_evolution_level = "High Co-evolution"

        logger.info(f"{datetime.now()} : END correlation pipeline_id {pipeline_id}")

    except Exception as e:

        logger.error(f"{datetime.now()} : correlation pipeline_id {pipeline_id} failed. Error: {e}")
        raise e

    return {"co_evolution_level": co_evolution_level, "pearson_correlation": data["pearson_correlation"]}

@router.post("/project_dimension")
def project_dimension(process: schemas.ProcessBase, db: Session = Depends(get_db)):
    db_pipeline = crud.get_pipeline_by_id(db, pipeline_id=process.pipeline_id)
    if db_pipeline is None:
        raise HTTPException(status_code=404, detail="Pipeline not found")

    pipeline_id = process.pipeline_id
    logger.info(f"{datetime.now()} : BEGIN project_dimension pipeline_id {pipeline_id}")

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
        data = get_json(os.path.join(BASE_LOG_PROJECT_DIMENSION, f"{project_result.id}.json"))

        logger.info(f"{datetime.now()} : END project_dimension pipeline_id {pipeline_id}")

    except Exception as e:

        logger.error(f"{datetime.now()} : project_dimension pipeline_id {pipeline_id} failed. Error: {e}")
        raise e

    return data

@router.post("/maintenance_activities")
def maintenance_activities(process: schemas.ProcessBase, db: Session = Depends(get_db)):
    db_pipeline = crud.get_pipeline_by_id(db, pipeline_id=process.pipeline_id)
    if db_pipeline is None:
        raise HTTPException(status_code=404, detail="Pipeline not found")

    pipeline_id = process.pipeline_id
    logger.info(f"{datetime.now()} : BEGIN maintenance_activities pipeline_id {pipeline_id}")

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
        data = get_json(os.path.join(BASE_SUMMARY_MAINTENANCE_ACTIVITIES, f"{project_result.id}.json"))

        logger.info(f"{datetime.now()} : END maintenance_activities pipeline_id {pipeline_id}")

    except Exception as e:

        logger.error(f"{datetime.now()} : maintenance_activities pipeline_id {pipeline_id} failed. Error: {e}")
        raise e

    return data

@router.post("/maintenance_activities_details")
def maintenance_activities_details(process: schemas.ProcessBase, db: Session = Depends(get_db)):
    db_pipeline = crud.get_pipeline_by_id(db, pipeline_id=process.pipeline_id)
    if db_pipeline is None:
        raise HTTPException(status_code=404, detail="Pipeline not found")

    pipeline_id = process.pipeline_id
    logger.info(f"{datetime.now()} : BEGIN maintenance_activities_details pipeline_id {pipeline_id}")

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
        data = get_maintenance_activities_details(project_result)

        logger.info(f"{datetime.now()} : END maintenance_activities_details pipeline_id {pipeline_id}")

    except Exception as e:

        logger.error(f"{datetime.now()} : maintenance_activities_details pipeline_id {pipeline_id} failed. Error: {e}")
        raise e

    return data