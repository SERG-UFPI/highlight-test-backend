import os
import warnings
from datetime import datetime

import pandas as pd
from scipy.stats import pearsonr

from app import crud, models
from app.constants import BASE_LOG_CLOC, BASE_PROJECTS, BASE_LOG_CO_EVOLUTION, BASE_SUMMARY_MAINTENANCE_ACTIVITIES, \
    BASE_LOG_PROJECT_DIMENSION, BASE_LOG_COMMITS, BASE_LOG_PERIOD_REVISIONS, BASE_LOG_REVISIONS, BASE_LOG_TEST_FILE, \
    BASE_LOG_MAINTENANCE_ACTIVITIES
from app.database import get_db
from app.dtos.commit_maintenance_activities_result import CommitMaintenanceActivitiesResult
from app.dtos.my_project_result import MyProjectResult
from app.enums import StatusEnum, StageEnum, LanguageEnum
from app.helpers.calculate_metrics_utils import get_maintenance_activities_repo, get_project_dimension_repo
from app.helpers.co_evolution_utils import check_coevolution
from app.helpers.utils import save_json, get_json, is_valid_date, is_zero_or_one
from app.logger_config import logger

VALID_REPOS = ['29078997', '32051890', '161001', '2206199', '75505125', '868282', '39718308', '12576526', '5844474', '235303', '10601208', '14964475', '15509440', '25800128', '22456440', '791299', '9891249', '4475900', '20878802', '388860', '72174164', '20532052', '1056713', '11718424', '42548553', '90468352', '738250', '4213474', '62256097', '2087064', '2629424', '9864166', '41173335', '55341469', '15714062', '2883574', '12201538', '2425099', '18596168', '113807330', '856112', '1327739', '59669326', '346893', '453037', '1939769', '28647218', '74253137', '105399035', '61425212', '443962', '102904613', '12191244', '54377519', '76100575', '41150635', '6521142', '145356', '81770291', '32411368', '460848', '23050594', '22636263', '924562', '100407304', '11591313', '6181245', '73864802', '30830689', '32304121', '33010673', '52522046', '252774', '116385203', '30369187', '44758360', '46755185', '78002587', '9274591', '91096213', '1613345', '1835758', '56126671', '16897008', '41822320', '10750139', '4995017', '52293126', '45195614', '76445704', '1135454', '2584777', '43618365', '42456996', '17941520', '16412440', '37799274', '10025737', '7480345', '41209174', '20473418', '2045207', '6944525', '4368712', '10416648', '44294727', '930571', '30449481', '8043551', '150938406', '9512610', '54973527', '141376301', '2543687', '1089149', '79564911', '86149', '27523092', '206459', '28738447', '16477702', '32866430', '1370858', '26873147', '50370190', '43158694', '42751387', '108050', '20675636', '9278888', '15289581', '66062805', '21985130', '1020601', '835466', '6140556', '9749905', '1072845', '1962219', '3250434', '34685800', '4063516', '4393933', '8710734', '37816257', '1937202', '111811015', '20415251', '11233996', '42457394', '64172164', '4354801', '2623406', '4600110', '100753606', '617210', '47767967', '4457770', '22684655', '5391743', '93584426', '98801926', '5757735', '208698479', '65308934', '31481933', '26836459', '327391', '2079469', '14259857', '22978651', '107676801', '61480983', '23050110', '15971461', '22165604', '283187', '49391150', '2183338', '148223447', '16687794', '210029529', '13691805', '148428318', '30357183', '41693388', '66079871', '46645199', '40049579', '538681', '24229101', '416272', '10188673', '2011647', '15745219', '71263775', '45662330', '4167742', '4812336', '46615164', '1215215', '37285717', '52948965', '101451042', '6441969', '47723400', '33494287', '30900836', '8836548', '17288475', '15491874', '24297039', '3701855', '4449830', '18877072', '34629135', '8912617', '47442408', '108805608', '30221142', '113922675', '49277180', '54335585', '43598554', '13421516', '42064055', '23023361', '23092563', '8655057', '11426278', '12402553', '8963857', '23953479', '10623444', '18812043', '25234505', '36859608', '7309368', '26004657', '2252722', '5217602', '4518881', '3440875', '1892699', '53612920', '7337389', '56475150', '914623', '12556145', '40514634', '4746018', '1671577', '34757137', '24290981', '20191684', '532252', '17924282', '8630443', '11314246', '25159454', '7446689', '19294390', '15743069', '7422694', '57914796', '7567133', '6280923', '66006332', '30879325', '129617905', '54150474', '110502136', '29021349', '16483856', '8704167', '80491509', '25695632', '33776257', '544113', '13459795', '37989340', '1934857', '42072677', '73427404', '13941998', '11625573', '45239038', '11099872', '4242408', '100695', '7548986', '5550552', '220418', '1548202', '17253775', '39149031', '6763587', '3431193', '448045', '4344257', '1864363', '3217621', '8875190', '42912130', '1398636', '2179920', '29843361', '12204147', '3055234', '7704544', '5660085', '4916869', '3244931', '2729639', '1398630', '2717549', '2641401', '12924368', '32482750', '6825542', '11478636', '1398648', '3378594', '24498056', '47495360', '17452080', '28257573', '761653', '330275', '13899674', '1398629', '1398660', '1129010', '14259390', '1381983', '42480275', '31295421', '2797951', '9193949', '576099', '677464', '569670', '14875475', '137515', '2253830', '48796179', '5893828', '1186228', '16238673', '4013840', '2641391', '39149689', '38116958', '2699935', '8708394', '11907506', '1398638', '11340559', '2894555', '1543827', '14732235', '2360755', '637935', '9004802', '2579314', '1420053', '7577142', '1398640', '4665416', '6660366', '1398628', '677467', '3192821', '1674552', '1398656', '16571051', '10728912', '1509011', '914985', '931033', '1582219', '4365645', '5627682', '26402582', '9738052', '7895524', '14976752', '2641404', '4549925', '42622303', '23056580', '1951136', '1398641', '3119126', '11323319', '8678290', '25275777', '859126', '1785452', '539751', '706295', '91253698', '71932349', '155220641', '123909654', '1390248', '3659275', '129936360', '5811958', '17982061', '154739597', '70908208', '28782747', '90194616', '1353927', '5078061', '130375797', '21273155', '83878269', '66474729', '5171600', '21467110', '5888353', '145848899', '77478378', '299862', '36506399', '145670234', '54980593', '184460', '1696822', '33702544', '363150', '124240220', '149430917', '20728281', '100401612', '1431547', '63476337', '122663163', '113111650', '60207695', '17066884', '51690353', '1284229', '35270176', '1310572', '101782647', '24561828', '145385156', '73759774', '55584626', '50063252', '33457642', '4008931', '1488139', '73872834', '24245737', '12052630', '5819063', '30367893', '9299325', '16667903', '776374', '251729', '62743585', '6198326', '5172439', '27283062', '31262911', '533328', '102246567', '3757435', '83821737', '1285095', '9265294', '11591264', '157198623', '24952819', '102252305', '4010596', '5133993', '44104712', '99224194', '75402138', '2471557', '4216175', '42377037', '34141361', '32623292', '107422373', '9185792', '7833168', '45247496', '62367558', '39464018', '381979', '21486287', '3038446', '50146229', '116817549', '3328572', '32247847', '105590837', '3605299', '24195339', '32215970', '21413198', '83716883', '91379993', '79252808', '36535156', '86941132', '112647343', '67361566', '73475252', '47851629', '71939872', '88897663', '86188653', '3618686', '93565582', '40403310', '52630616', '66944590', '56315715']

def clean_data(string):
    """
    Clean the data by removing single quotes.
    :param string:
    :return:
    """
    return str(string).replace("'", "")

def import_repositories():
    """
    Import repositories from a CSV file and save them to the database.
    :return:
    """
    df = pd.read_csv(BASE_PROJECTS+'projectinfo.csv', sep=',')

    db = next(get_db())

    now = datetime.now()

    for index, row in df.iterrows():
        project_id = clean_data(row["id"])
        if project_id in VALID_REPOS:
            logger.info(f"Processing project {project_id}")
            clone_url = clean_data(row["clone_url"])

            db_repository = crud.get_repository_by_clone_url(db, clone_url=clone_url)
            if db_repository is None:
                db_repository = models.Repository()
                db_repository.owner = 'SERG-UFPI'
                db_repository.default_branch = clean_data(row["default_branch"])
                db_repository.clone_url = clean_data(row["clone_url"])
                db_repository.created_at = now
                db.add(db_repository)
                db.commit()
                db.refresh(db_repository)

                db_additional_data = models.AdditionalData()
                db_additional_data.name = clean_data(row["name"])
                db_additional_data.full_name = clean_data(row["full_name"])
                db_additional_data.language = clean_data(row["language"])
                db_additional_data.forks_count = clean_data(row["forks_count"])
                db_additional_data.open_issues_count = clean_data(row["open_issues_count"])
                db_additional_data.created_at = now
                db_additional_data.pushed_at = clean_data(row["pushed_at"])
                db_additional_data.external_id = project_id
                db_additional_data.repository = db_repository.id
                db_additional_data.uses_external_id = True
                db.add(db_additional_data)
                db.commit()
                db.refresh(db_additional_data)

                db_pipeline = models.Pipeline()
                db_pipeline.repository = db_repository.id
                db_pipeline.stage = StageEnum.CO_EVOLUTION_ANALYSIS
                db_pipeline.status = StatusEnum.COMPLETED
                db_pipeline.created_at = now
                db_pipeline.updated_at = now
                db_pipeline.share_consent = True
                db.add(db_pipeline)
                db.commit()
                db.refresh(db_pipeline)

                logger.info(f"Repository {db_repository.id} created")



def generate_cloc_series_history():
    """
    @deprecated
    Generate the cloc series history for each project in the CSV file.
    :return:
    """
    df = pd.read_csv(BASE_PROJECTS+'projectinfo.csv', sep=',')

    production_code_list = get_json(os.path.join(BASE_LOG_CLOC, "False_production_code_list.json"))

    test_code_list = get_json(os.path.join(BASE_LOG_CLOC, "False_test_code_list.json"))

    for index, row in df.iterrows():
        project_id = clean_data(row["id"])
        if project_id in VALID_REPOS:
            logger.info(f"Processing project {project_id}")
            production_code_path = BASE_LOG_CLOC + f"{project_id}_production_code_list.json"
            test_code_path = BASE_LOG_CLOC + f"{project_id}_test_code_list.json"

            if not os.path.exists(production_code_path):
                ploc_list = get_code_series_item_as_list(production_code_list, project_id)

                if ploc_list is not None:
                    save_json(BASE_LOG_CLOC, f"{project_id}_production_code_list", ploc_list)

            if not os.path.exists(test_code_path):
                tloc_list = get_code_series_item_as_list(test_code_list, project_id)

                if tloc_list is not None:
                    save_json(BASE_LOG_CLOC, f"{project_id}_test_code_list", tloc_list)

def get_code_series_item_as_list(list, id):
    """
    Get the code series item as a list based on the id.
    :param list:
    :param id:
    :return:
    """
    for item in list:
        if item["id"] == id:
            return [item]
    return None

def generate_co_evolution_analysis():
    """
    @deprecated
    Generate the co-evolution analysis for each project in the CSV file.
    :return:
    """
    df = pd.read_csv(BASE_PROJECTS+'projectinfo.csv', sep=',')

    db = next(get_db())

    for index, row in df.iterrows():
        project_id = clean_data(row["id"])
        if project_id in VALID_REPOS:
            logger.info(f"Processing project {project_id}")
            clone_url = clean_data(row["clone_url"])

            db_repository = crud.get_repository_by_clone_url(db, clone_url=clone_url)
            if db_repository:

                db_additional_data = crud.get_additional_data_by_repository(db, repository_id=db_repository.id)

                project_result = MyProjectResult(db_additional_data, None)

                production_code_list = get_json(
                    os.path.join(BASE_LOG_CLOC, f"{project_result.id}_production_code_list.json"))

                test_code_list = get_json(os.path.join(BASE_LOG_CLOC, f"{project_result.id}_test_code_list.json"))

                pcc_val = check_coevolution(production_code_list[0]['timeseries'], test_code_list[0]['timeseries'])

                save_json(BASE_LOG_CO_EVOLUTION, str(project_result.id), {"pearson_correlation": pcc_val})


def generate_metrics():
    """
    @deprecated
    Generate metrics for each project in the CSV file.
    :return:
    """
    df = pd.read_csv(BASE_PROJECTS+'projectinfo.csv', sep=',')

    db = next(get_db())

    for index, row in df.iterrows():
        project_id = clean_data(row["id"])
        if project_id in VALID_REPOS:
            logger.info(f"Processing project {project_id}")
            clone_url = clean_data(row["clone_url"])

            db_repository = crud.get_repository_by_clone_url(db, clone_url=clone_url)
            if db_repository:

                db_additional_data = crud.get_additional_data_by_repository(db, repository_id=db_repository.id)

                project_result = MyProjectResult(db_additional_data, None)

                data_repo = get_project_dimension_repo(project_result)
                n_commits = data_repo["n_commits"]
                n_devs = data_repo["n_authors"]

                n_forks_count = project_result.forks_count
                n_open_issues_count = project_result.open_issues_count

                save_json(BASE_LOG_PROJECT_DIMENSION, str(project_result.id), {
                    "n_commits": n_commits, "n_devs": n_devs, "n_forks_count": n_forks_count,
                    "n_open_issues_count": n_open_issues_count
                })

                data_repo = get_maintenance_activities_repo(project_result)

                result_repo_test_sum = data_repo["n_corrective"] + data_repo["n_adaptive"] + data_repo["n_perfective"]

                n_corrective = data_repo["n_corrective"] * 100 / result_repo_test_sum
                n_adaptive = data_repo["n_adaptive"] * 100 / result_repo_test_sum
                n_perfective = data_repo["n_perfective"] * 100 / result_repo_test_sum
                n_multi = data_repo["n_multi"] * 100 / result_repo_test_sum

                save_json(BASE_SUMMARY_MAINTENANCE_ACTIVITIES, str(project_result.id), {
                    "n_corrective": n_corrective, "n_adaptive": n_adaptive, "n_perfective": n_perfective,
                    "n_multi": n_multi
                })

def save_commits():
    """
    Save commits from a CSV file to the database.
    :return:
    """
    df = pd.read_csv(BASE_PROJECTS+'projectinfo.csv', sep=',')

    db = next(get_db())

    for index, row in df.iterrows():
        project_id = clean_data(row["id"])
        if project_id in VALID_REPOS:
            logger.info(f"Processing project {project_id}")
            clone_url = clean_data(row["clone_url"])

            db_repository = crud.get_repository_by_clone_url(db, clone_url=clone_url)
            if db_repository:
                db_additional_data = crud.get_additional_data_by_repository(db, repository_id=db_repository.id)

                db_pipeline = crud.get_pipelines_by_repository(db, repository_id=db_repository.id)[0]

                project_result = MyProjectResult(db_additional_data, db_pipeline.id)
                project_result.id = clean_data(db_additional_data.external_id)

                logger.info(f"Processing pipeline {db_pipeline.id}")

                if crud.exits_commits_by_pipeline(db, db_pipeline.id):
                    logger.info(f"Commits already exist for project_id {project_id} and pipeline.")
                    continue

                # ["hash", "author", "committer", "date", "msg"]
                m_file = open(BASE_LOG_COMMITS + str(project_result.id) + '.csv', 'r', encoding='latin-1')
                for m_row in m_file:
                    row_data = m_row.split(";")
                    if len(row_data) > 5:

                        commit_data = {
                            "hash": row_data[0],
                            "author_name": row_data[1],
                            "committer_name": row_data[2],
                            "author_date": row_data[3],
                            "message": row_data[4],
                            "pipeline_id": db_pipeline.id
                        }

                        if is_valid_date(row_data[3]):
                            crud.create_commit(db, commit_data)
                        else:
                            logger.error(f"Invalid date in create_commit: {row_data[3]}")

            logger.info(f"End project {project_id}")

def save_code_metrics():
    """
    Save code metrics from a CSV file to the database.
    :return:
    """
    df = pd.read_csv(BASE_PROJECTS+'projectinfo.csv', sep=',')

    db = next(get_db())

    for index, row in df.iterrows():
        project_id = clean_data(row["id"])
        if project_id in VALID_REPOS:
            logger.info(f"Processing project {project_id}")
            clone_url = clean_data(row["clone_url"])

            db_repository = crud.get_repository_by_clone_url(db, clone_url=clone_url)
            if db_repository:
                db_additional_data = crud.get_additional_data_by_repository(db, repository_id=db_repository.id)

                db_pipeline = crud.get_pipelines_by_repository(db, repository_id=db_repository.id)[0]

                project_result = MyProjectResult(db_additional_data, db_pipeline.id)
                project_result.id = clean_data(db_additional_data.external_id)

                logger.info(f"Processing pipeline {db_pipeline.id}")

                if crud.exits_code_metrics_by_pipeline(db, db_pipeline.id):
                    logger.info(f"CodeMetrics already exist for project_id {project_id} and pipeline.")
                    continue

                production_code_list = get_json(os.path.join(BASE_LOG_CLOC, f"{project_result.id}_production_code_list.json"))

                if not production_code_list or 'timeseries' not in production_code_list[0]:
                    logger.error(f"Production code list or timeseries not found for project {project_id}")
                    continue

                test_code_list = get_json(os.path.join(BASE_LOG_CLOC, f"{project_result.id}_test_code_list.json"))

                if not test_code_list or 'timeseries' not in test_code_list[0]:
                    logger.error(f"Test code list or timeseries not found for project {project_id}")
                    continue

                ploc_entry = {
                    "full_name": production_code_list[0]['full_name'],
                    "timeseries": production_code_list[0]['timeseries'],
                    "metric_type": "production",
                    "pipeline_id": db_pipeline.id
                }

                tloc_entry = {
                    "full_name": production_code_list[0]['full_name'],
                    "timeseries": test_code_list[0]['timeseries'],
                    "metric_type": "test",
                    "pipeline_id": db_pipeline.id
                }

                crud.create_code_metrics(db, ploc_entry)
                crud.create_code_metrics(db, tloc_entry)

                logger.info(f"End project {project_id}")

def save_competence_and_base_items():
    """
    Save competence and base items from a CSV file to the database.
    :return:
    """
    df = pd.read_csv(BASE_PROJECTS+'projectinfo.csv', sep=',')

    db = next(get_db())

    for index, row in df.iterrows():
        project_id = clean_data(row["id"])
        if project_id in VALID_REPOS:
            logger.info(f"Processing project {project_id}")
            clone_url = clean_data(row["clone_url"])

            db_repository = crud.get_repository_by_clone_url(db, clone_url=clone_url)
            if db_repository:
                db_additional_data = crud.get_additional_data_by_repository(db, repository_id=db_repository.id)

                db_pipeline = crud.get_pipelines_by_repository(db, repository_id=db_repository.id)[0]

                project_result = MyProjectResult(db_additional_data, db_pipeline.id)
                project_result.id = clean_data(db_additional_data.external_id)

                logger.info(f"Processing pipeline {db_pipeline.id}")

                if not crud.exits_competences_by_pipeline(db, db_pipeline.id):
                    revisions = get_json(os.path.join(BASE_LOG_PERIOD_REVISIONS, str(project_result.id) + '.json'))

                    if revisions:
                        for competence in revisions:
                            db_competence = {
                                "competence": competence,
                                "pipeline_id": db_pipeline.id
                            }

                            crud.create_competence(db, db_competence)

                    else:
                        logger.error(f"Revision not found for project {project_id}")

                else:
                    logger.info(f"Revision already exist for project_id {project_id} and pipeline.")


                if not crud.exits_base_items_by_pipeline(db, db_pipeline.id):
                    commits = get_json(os.path.join(BASE_LOG_REVISIONS, str(project_result.id) + '.json'))

                    if commits:
                        for item in commits:
                            db_base = {
                                "base_item": item,
                                "pipeline_id": db_pipeline.id
                            }

                            crud.create_base_item(db, db_base)

                    else:
                        logger.error(f"Commits not found for project {project_id}")

                else:
                    logger.info(f"Commits already exist for project_id {project_id} and pipeline.")

                logger.info(f"End project {project_id}")


def save_test_datas():
    """
    Save test data from a CSV file to the database.
    :return:
    """
    df = pd.read_csv(BASE_PROJECTS+'projectinfo.csv', sep=',')

    db = next(get_db())

    for index, row in df.iterrows():
        project_id = clean_data(row["id"])
        if project_id in VALID_REPOS:
            logger.info(f"Processing project {project_id}")
            clone_url = clean_data(row["clone_url"])

            db_repository = crud.get_repository_by_clone_url(db, clone_url=clone_url)
            if db_repository:
                db_additional_data = crud.get_additional_data_by_repository(db, repository_id=db_repository.id)

                db_pipeline = crud.get_pipelines_by_repository(db, repository_id=db_repository.id)[0]

                project_result = MyProjectResult(db_additional_data, db_pipeline.id)
                project_result.id = clean_data(db_additional_data.external_id)

                logger.info(f"Processing pipeline {db_pipeline.id}")

                """Details will be presented only for Java projects initially."""
                if project_result.project_language != LanguageEnum.JAVA:
                    logger.info(f"Skipping project_id {project_id}: The detected language is not Java.")
                    continue

                if crud.exits_test_datas_by_pipeline(db, db_pipeline.id):
                    logger.info(f"TestData already exist for project_id {project_id} and pipeline.")
                    continue

                revisions = crud.get_competences_by_pipeline(db, db_pipeline.id)
                revision_length = len(revisions)

                commit_history = range(revision_length)

                for commit_order in commit_history:

                    test_path_log = os.path.join(BASE_LOG_TEST_FILE, str(project_result.id), str(commit_order), (str(project_result.id) + '.csv'))

                    if not os.path.exists(test_path_log):
                        continue

                    m_file = open(test_path_log, 'r', encoding='latin-1')
                    for m_row in m_file:
                        row_data = m_row.split(",")

                        if len(row_data) > 4:

                            db_test_data = {
                                "file_path": row_data[1],
                                "is_test_file": is_zero_or_one(row_data[2]),
                                "has_test_import": is_zero_or_one(row_data[3]),
                                "has_test_call": is_zero_or_one(row_data[4]),
                                "pipeline_id": db_pipeline.id,
                                "commit_order": commit_order
                            }

                            crud.create_test_data(db, db_test_data)

            logger.info(f"End project {project_id}")

def save_project_dimensions():
    """
    Save project dimensions from a CSV file to the database.
    :return:
    """
    df = pd.read_csv(BASE_PROJECTS+'projectinfo.csv', sep=',')

    db = next(get_db())

    for index, row in df.iterrows():
        project_id = clean_data(row["id"])
        if project_id in VALID_REPOS:
            logger.info(f"Processing project {project_id}")
            clone_url = clean_data(row["clone_url"])

            db_repository = crud.get_repository_by_clone_url(db, clone_url=clone_url)
            if db_repository:
                db_additional_data = crud.get_additional_data_by_repository(db, repository_id=db_repository.id)

                db_pipeline = crud.get_pipelines_by_repository(db, repository_id=db_repository.id)[0]

                project_result = MyProjectResult(db_additional_data, db_pipeline.id)
                project_result.id = clean_data(db_additional_data.external_id)

                logger.info(f"Processing pipeline {db_pipeline.id}")

                if not crud.exits_project_dimension_by_pipeline(db, db_pipeline.id):
                    project_dimensions = get_json(os.path.join(BASE_LOG_PROJECT_DIMENSION, str(project_result.id) + '.json'))

                    if project_dimensions:
                        project_dimension_entry = {
                            "n_commits": project_dimensions["n_commits"],
                            "n_devs": project_dimensions["n_devs"],
                            "n_forks_count": project_dimensions["n_forks_count"],
                            "n_open_issues_count": project_dimensions["n_open_issues_count"],
                            "pipeline_id": db_pipeline.id
                        }

                        crud.create_project_dimension(db, project_dimension_entry)

                    else:
                        logger.error(f"ProjectDimension not found for project {project_id}")

                else:
                    logger.info(f"ProjectDimension already exist for project_id {project_id} and pipeline.")

                logger.info(f"End project {project_id}")

def save_correlation():
    """
    Save correlation data from a CSV file to the database.
    :return:
    """
    df = pd.read_csv(BASE_PROJECTS+'projectinfo.csv', sep=',')

    db = next(get_db())

    for index, row in df.iterrows():
        project_id = clean_data(row["id"])
        if project_id in VALID_REPOS:
            logger.info(f"Processing project {project_id}")
            clone_url = clean_data(row["clone_url"])

            db_repository = crud.get_repository_by_clone_url(db, clone_url=clone_url)
            if db_repository:
                db_additional_data = crud.get_additional_data_by_repository(db, repository_id=db_repository.id)

                db_pipeline = crud.get_pipelines_by_repository(db, repository_id=db_repository.id)[0]

                project_result = MyProjectResult(db_additional_data, db_pipeline.id)
                project_result.id = clean_data(db_additional_data.external_id)

                logger.info(f"Processing pipeline {db_pipeline.id}")

                if not crud.exits_correlation_by_pipeline(db, db_pipeline.id):
                    pearson_correlation = get_json(os.path.join(BASE_LOG_CO_EVOLUTION, str(project_result.id) + '.json'))

                    if pearson_correlation:
                        correlation = {
                            "pearson_correlation": pearson_correlation["pearson_correlation"],
                            "pipeline_id": db_pipeline.id,
                        }

                        crud.create_correlation(db, correlation)

                    else:
                        logger.error(f"Correlation not found for project {project_id}")

                else:
                    logger.info(f"Correlation already exist for project_id {project_id} and pipeline.")

                logger.info(f"End project {project_id}")

def save_insights():
    """
    Save insights data from a CSV file to the database.
    :return:
    """
    df = pd.read_csv(BASE_PROJECTS+'projectinfo.csv', sep=',')

    db = next(get_db())

    for index, row in df.iterrows():
        project_id = clean_data(row["id"])
        if project_id in VALID_REPOS:
            logger.info(f"Processing project {project_id}")
            clone_url = clean_data(row["clone_url"])

            db_repository = crud.get_repository_by_clone_url(db, clone_url=clone_url)
            if db_repository:
                db_additional_data = crud.get_additional_data_by_repository(db, repository_id=db_repository.id)

                db_pipeline = crud.get_pipelines_by_repository(db, repository_id=db_repository.id)[0]

                project_result = MyProjectResult(db_additional_data, db_pipeline.id)
                project_result.id = clean_data(db_additional_data.external_id)

                logger.info(f"Processing pipeline {db_pipeline.id}")

                if not crud.exits_insights_by_pipeline(db, db_pipeline.id):

                    insight = get_json(os.path.join(BASE_LOG_CLOC, f"{project_id}_cluster_insights.json"))

                    if insight:
                        insight_entry = {
                            "pipeline_id": db_pipeline.id,
                            "generated_text": insight["generated_text"]
                        }

                        crud.create_insights(db, insight_entry)

                    else:
                        logger.error(f"Insights not found for project {project_id}")

                else:
                    logger.info(f"Insights already exist for project_id {project_id} and pipeline.")

                logger.info(f"End project {project_id}")

def save_commit_message_item():
    """
    Save commit message items from a CSV file to the database.
    :return:
    """
    df = pd.read_csv(BASE_PROJECTS+'projectinfo.csv', sep=',')

    db = next(get_db())

    for index, row in df.iterrows():
        project_id = clean_data(row["id"])
        if project_id in VALID_REPOS:
            logger.info(f"Processing project {project_id}")
            clone_url = clean_data(row["clone_url"])

            db_repository = crud.get_repository_by_clone_url(db, clone_url=clone_url)
            if db_repository:
                db_additional_data = crud.get_additional_data_by_repository(db, repository_id=db_repository.id)

                db_pipeline = crud.get_pipelines_by_repository(db, repository_id=db_repository.id)[0]

                project_result = MyProjectResult(db_additional_data, db_pipeline.id)
                project_result.id = clean_data(db_additional_data.external_id)

                logger.info(f"Processing pipeline {db_pipeline.id}")

                if crud.exits_commit_message_items_by_pipeline(db, db_pipeline.id):
                    logger.info(f"CommitMessageItem already exist for project_id {project_id} and pipeline.")
                    continue

                m_file = open(BASE_LOG_MAINTENANCE_ACTIVITIES + str(project_result.id) + '.csv', 'r', encoding='latin-1')
                for m_row in m_file:
                    commit_message_item = CommitMaintenanceActivitiesResult()
                    csv_line = m_row.split(';')

                    if len(csv_line) < 17:
                        continue

                    commit_message_item.set_from_csv(csv_line)

                    commit_message_item.pipeline_id = db_pipeline.id

                    crud.create_commit_message_item(db, commit_message_item.to_dict())

            logger.info(f"End project {project_id}")

def save_maintenance_activity_summaries():
    """
    Save maintenance activity summaries from a CSV file to the database.
    :return:
    """
    df = pd.read_csv(BASE_PROJECTS+'projectinfo.csv', sep=',')

    db = next(get_db())

    for index, row in df.iterrows():
        project_id = clean_data(row["id"])
        if project_id in VALID_REPOS:
            logger.info(f"Processing project {project_id}")
            clone_url = clean_data(row["clone_url"])

            db_repository = crud.get_repository_by_clone_url(db, clone_url=clone_url)
            if db_repository:
                db_additional_data = crud.get_additional_data_by_repository(db, repository_id=db_repository.id)

                db_pipeline = crud.get_pipelines_by_repository(db, repository_id=db_repository.id)[0]

                project_result = MyProjectResult(db_additional_data, db_pipeline.id)

                logger.info(f"Processing pipeline {db_pipeline.id}")

                if crud.exits_maintenance_activity_summary_by_pipeline(db, db_pipeline.id):
                    logger.info(f"MaintenanceActivitySummary already exist for project_id {project_id} and pipeline.")
                    continue

                data_repo = get_maintenance_activities_repo(project_result, db)

                result_repo_test_sum = data_repo["n_corrective"] + data_repo["n_adaptive"] + data_repo["n_perfective"]

                n_corrective = data_repo["n_corrective"] * 100 / result_repo_test_sum
                n_adaptive = data_repo["n_adaptive"] * 100 / result_repo_test_sum
                n_perfective = data_repo["n_perfective"] * 100 / result_repo_test_sum
                n_multi = data_repo["n_multi"] * 100 / result_repo_test_sum

                maintenance_activity_summary = {
                    "n_corrective": n_corrective,
                    "n_adaptive": n_adaptive,
                    "n_perfective": n_perfective,
                    "n_multi": n_multi,
                    "pipeline_id": db_pipeline.id
                }

                crud.create_maintenance_activity_summary(db, maintenance_activity_summary)

            logger.info(f"End project {project_id}")
