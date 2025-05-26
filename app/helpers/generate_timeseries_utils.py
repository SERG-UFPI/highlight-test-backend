from datetime import datetime

from app import crud
from app.constants import *
from app.crud import get_tests_data_by_pipeline
from app.helpers.string_utils import get_comma_separated_names
from app.helpers.system_utils import is_windows
from app.helpers.validation_utils import parse_int
from app.logger_config import logger


def process_cloc_history(base_git_path, loc_path_log):
    """
    Process the cloc history for a given git repository.
    :param base_git_path:
    :param loc_path_log:
    :return:
    """

    path_full_log = os.path.join(loc_path_log, "cloc.log")

    if is_windows():
        command = "cd {path_full_git} && {cmd_cloc} {path_full_git} --by-file --csv > {path_full_log}".format(
            path_full_git=base_git_path, cmd_cloc=EXTERNAL_DIR+"cloc.exe", path_full_log=path_full_log)
    else:
        command = "cd {path_full_git} && cloc {path_full_git} --by-file --csv > {path_full_log}".format(
            path_full_git=base_git_path, path_full_log=path_full_log)

    logger.info(command)
    os.system(command)

def cloc_series(pipeline_id, classify_test_based_on_function, db):
    """
    Process the cloc series for a given pipeline.
    :param pipeline_id:
    :param classify_test_based_on_function:
    :param db:
    :return:
    """
    logger.info("{now} : BEGIN git log process_cloc: {path_git} \n".format(now=datetime.now(), path_git=pipeline_id))

    ploc_item = []
    tloc_item = []

    base_itens = crud.get_base_items_by_pipeline(db, pipeline_id)
    revisions = [revision.base_item for revision in base_itens]

    revision_length = len(revisions)
    commit_selected = range(revision_length)

    test_datas = get_tests_data_by_pipeline(db, pipeline_id)

    test_data_by_commit_order = {}
    for data in test_datas:
        if data.commit_order not in test_data_by_commit_order:
            test_data_by_commit_order[data.commit_order] = []
        test_data_by_commit_order[data.commit_order].append(data)

    for commit_order in commit_selected:

        details_data = []

        ploc_sum = 0
        tloc_sum = 0

        filtered_test_datas = test_data_by_commit_order.get(commit_order, [])

        if filtered_test_datas is None or len(filtered_test_datas) == 0:
            ploc_item.append(ploc_sum)
            tloc_item.append(tloc_sum)
            continue

        if classify_test_based_on_function:
            t_files = [data.file_path.replace('\\', '/').replace('//', '/') for data in filtered_test_datas if data.has_test_call == 1]

        else:
            t_files = [data.file_path.replace('\\', '/').replace('//', '/') for data in filtered_test_datas if data.is_test_file == 1]

        opened_file = open(os.path.join(BASE_LOG_LOC, str(pipeline_id), str(commit_order), 'cloc.log'), "r",
                           encoding="latin-1")

        for line in opened_file:

            if line.find(BASE_PROJECTS_FOLDER_NAME) == -1 and line.find(IMPORTED_PROJECTS_FOLDER_NAME) == -1:
                continue

            # language;filename;blank;comment;code;
            line_data = line.split(',')

            language = line_data[0]
            path_query = get_comma_separated_names(line_data, 5, 1, 2).replace('\\', '/').replace('//', '/')
            value = parse_int(line_data[-1].replace('\n', ''))

            extension = path_query.rpartition(".")[-1]
            if extension not in FILE_EXTENSION_ACCEPTED:
                continue

            is_test_file = path_query in t_files

            if is_test_file:
                tloc_sum = tloc_sum + value
            else:
                ploc_sum = ploc_sum + value

            details_data.append({"language": language, "commit_order": commit_order,
                                                   "pipeline_id": str(pipeline_id),
                                                   "path": path_query, "loc": value})

        crud.create_all_code_distribution_details(db, details_data)

        ploc_item.append(ploc_sum)
        tloc_item.append(tloc_sum)

        opened_file.close()

    logger.info("{now} : END git log process_cloc: {path_git} \n".format(now=datetime.now(), path_git=str(pipeline_id)))

    return [ploc_item, tloc_item]