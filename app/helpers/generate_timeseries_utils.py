from datetime import datetime

from app.constants import *
from app.helpers.utils import get_json, get_comma_separated_names, is_windows, parse_int


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

    print(command)
    os.system(command)

def get_files(project_id, commit_order, classify_test_based_on_function):
    """
    Get the files from the git log.
    :param project_id:
    :param commit_order:
    :param classify_test_based_on_function:
    :return:
    """
    t_path = os.path.join(BASE_LOG_TEST_FILE, str(project_id), str(commit_order), str(project_id) + ".csv")

    p_files = []
    t_files = []

    if not os.path.exists(t_path):
        return {"p_files": p_files, "t_files": t_files}

    with open(t_path, newline='', encoding="latin-1") as csv_file:
        for csv_line in csv_file:
            line_data = csv_line.split(',')
            # tratar a ultima linha
            if '\n' in line_data[0]:
                continue

            # tratar a ultima linha
            if '\r' in line_data[0]:
                continue

            if len(line_data) < 5:
                continue

            base_git = line_data[0]
            path_file = get_comma_separated_names(line_data, 5, 1, 2)

            if classify_test_based_on_function:
                is_test_file = line_data[-1]
            else:
                is_test_file = line_data[-3]

            path_full_file = os.path.join(BASE_PROJECTS, project_id, base_git, path_file)

            if parse_int(is_test_file) == 1:
                t_files.append(path_full_file.replace('\\', '/').replace('//', '/'))

            else:
                p_files.append(path_full_file.replace('\\', '/').replace('//', '/'))

    return {"p_files": p_files, "t_files": t_files}

def cloc_series(project_id, classify_test_based_on_function):
    """
    Process the cloc series for a given git repository.
    :param project_id:
    :param classify_test_based_on_function:
    :return:
    """
    print("{now} : BEGIN git log process_cloc: {path_git} \n".format(now=datetime.now(), path_git=project_id))

    ploc_item = []
    tloc_item = []

    revisions = get_json(os.path.join(BASE_LOG_REVISIONS, str(project_id) + '.json'))
    revision_length = len(revisions)
    commit_selected = range(revision_length)
    for commit_order in commit_selected:

        ploc_sum = 0
        tloc_sum = 0

        t_path = os.path.join(BASE_LOG_TEST_FILE, str(project_id), str(commit_order), str(project_id) + ".csv")

        if not os.path.exists(t_path):
            ploc_item.append(ploc_sum)
            tloc_item.append(tloc_sum)
            continue

        files_data = get_files(project_id, commit_order, classify_test_based_on_function)

        p_files = files_data["p_files"]
        t_files = files_data["t_files"]

        valid_cloc = False
        opened_file = open(os.path.join(BASE_LOG_LOC, str(project_id), str(commit_order), 'cloc.log'), "r",
                           encoding="latin-1")

        for line in opened_file:

            if line.find(BASE_PROJECTS_FOLDER_NAME) == -1:
                continue

            if not valid_cloc:
                valid_cloc = True

            # language;filename;blank;comment;code;
            line_data = line.split(',')

            path_query = get_comma_separated_names(line_data, 5, 1, 2).replace('\\', '/').replace('//', '/')
            value = parse_int(line_data[-1].replace('\n', ''))

            extension = path_query.rpartition(".")[-1]
            if extension not in FILE_EXTENSION_ACCEPTED:
                continue

            if path_query in p_files:
                ploc_sum = ploc_sum + value
                continue

            if path_query in t_files:
                tloc_sum = tloc_sum + value
                continue

        ploc_item.append(ploc_sum)
        tloc_item.append(tloc_sum)

        opened_file.close()

    print("{now} : END git log process_cloc: {path_git} \n".format(now=datetime.now(), path_git=str(project_id)))

    return [ploc_item, tloc_item]