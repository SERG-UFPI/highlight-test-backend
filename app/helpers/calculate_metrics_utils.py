from datetime import datetime

from .. import crud
from ..constants import *
from ..crud import get_commits_by_pipeline
from ..libs.commit_classification_master.language_utils import match
from ..libs.commit_classification_master.adaptive_model import is_adaptive, build_adaptive_action_regex
from ..libs.commit_classification_master.corrective_model import is_fix,build_bug_fix_regex
from ..libs.commit_classification_master.refactor_model import built_is_refactor, build_perfective_regex, build_refactor_regex
import re

from ..logger_config import logger


def get_project_dimension_repo(project_result, db):
    """
    Get the project dimension from the repository.
    :param project_result:
    :param db:
    :return:
    """

    logger.info("{now} : BEGIN get_data_repo {base_git_path} \n".format(now=datetime.now(),
                                                                  base_git_path=str(project_result.id)))

    commits = get_commits_by_pipeline(db, str(project_result.id))

    if commits is None or len(commits) == 0:
        return 0

    commits_list = [commit.hash for commit in commits]
    authors_list = [commit.author_name for commit in commits]

    authors = set(authors_list)

    logger.info("{now} : END get_data_repo {base_git_path}\n".format(now=datetime.now(), base_git_path=str(project_result.id)))
    return {"n_commits": len(commits_list), "n_authors": len(authors)}

def get_commits(project_result):
    """
    Get the commit messages from the repository.
    :param project_result:
    :return:
    """
    rows = []
    if not os.path.exists(BASE_LOG_COMMITS + str(project_result.id) + '.csv'):
        return 0

    # ["hash", "author", "committer", "date", "msg"]
    m_file = open(BASE_LOG_COMMITS + str(project_result.id) + '.csv', 'r', encoding='latin-1')
    for m_row in m_file:
        row_data = m_row.split(";")
        if len(row_data) > 5:
            rows.append({"hash": row_data[0],"author": row_data[1],"committer": row_data[2],"date": row_data[3],"msg": row_data[4]})

    return rows

def get_maintenance_activities_details(project_result):
    """
    Get the maintenance activities details from the repository.
    :param project_result:
    :return:
    """
    rows = []

    if not os.path.exists(BASE_LOG_MAINTENANCE_ACTIVITIES + str(project_result.id) + '.csv'):
        return 0

    m_file = open(BASE_LOG_MAINTENANCE_ACTIVITIES + str(project_result.id) + '.csv', 'r', encoding='latin-1')

    for row in m_file:
        row_data = row.split(';')

        if len(row_data) < 17:
            continue

        rows.append({"hash": row_data[0],
                     "message": row_data[1],
                     "bug_fix_regex_count": row_data[2],
                     "adaptive_regex_count": row_data[3],
                     "adaptive_by_negation_regex_count": row_data[4],
                     "perfective_regex_count": row_data[5],
                     "refactor_regex_count": row_data[6],
                     "perfective_in_text": row_data[12],
                     "refactor_in_text": row_data[13],
                     "adaptive_in_text": row_data[14],
                     "adaptive_by_negation_in_text": row_data[15],
                     "corrective_in_text": row_data[16],
        })

    return rows


def get_devs_group_by_commits(project_result):
    """
    Get the developers grouped by the number of commits they made.
    :param project_result:
    :return:
    """
    logger.info("{now} : BEGIN get_devs_group_by_commits {base_git_path} \n".format(now=datetime.now(),
                                                                  base_git_path=str(project_result.id)))

    if not os.path.exists(BASE_LOG_COMMITS + str(project_result.id) + '.csv'):
        return 0

    # ["hash", "author", "committer", "date", "msg"]
    m_file = open(BASE_LOG_COMMITS + str(project_result.id) + '.csv', 'r', encoding='latin-1')
    authors_list = []
    for m_row in m_file:
        row = m_row.split(";")
        if len(row) > 5:
            author_found = False
            for author in authors_list:
                if author["name"] == row[1]:
                    author["commits"] += 1
                    author_found = True
                    break

            if not author_found:
                authors_list.append({"name": row[1], "commits": 1})

    logger.info("{now} : END get_devs_group_by_commits {base_git_path}\n".format(now=datetime.now(), base_git_path=str(project_result.id)))
    return authors_list

def corrective_classifier(commit_message):
    """
    Classify the commit message as corrective or not.
    :param commit_message:
    :return:
    """
    text = commit_message.message

    commit_message.is_corrective = is_fix(text)
    commit_message.corrective_in_text = re.findall(build_bug_fix_regex(), text)
    valid_num = len(commit_message.corrective_in_text)
    commit_message.bug_fix_regex_count = valid_num

    return commit_message


def adaptive_classifier(commit_message):
    """
    Classify the commit message as adaptive or not.
    :param commit_message:
    :return:
    """
    text = commit_message.message

    commit_message.is_adaptive = is_adaptive(text)
    commit_message.adaptive_in_text = re.findall(build_adaptive_action_regex(), text)
    valid_num = len(commit_message.adaptive_in_text)
    commit_message.adaptive_regex_count = valid_num

    return commit_message


def adaptive_by_negation_classifier(commit_message):
    """
    Classify the commit message as adaptive by negation or not.
    :param commit_message:
    :return:
    """
    text = commit_message.message

    commit_message.is_adaptive_by_negation = (is_fix(text) == 0
                                              and built_is_refactor(text) == 0
                                              and match(text, build_perfective_regex()) == 0)
    # commitMessage.adaptive_by_negation_in_text = re.findall(build_adaptive_action_regex(), text)
    # valid_num = len(commitMessage.adaptive_in_text)
    # commitMessage.bug_fix_regex_count = valid_num

    return commit_message


def perfective_classifier(commit_message):
    """
    Classify the commit message as perfective or not.
    :param commit_message:
    :return:
    """
    text = commit_message.message

    commit_message.is_perfective = ((match(text, build_perfective_regex())) +
                                    (match(text, build_refactor_regex())) > 0)
    # commitMessage.perfective_in_text = re.findall(build_adaptive_action_regex(), text)
    # valid_num = len(commitMessage.adaptive_in_text)
    # commitMessage.bug_fix_regex_count = valid_num

    return commit_message


def refactor_classifier(commit_message):
    """
    Classify the commit message as refactor or not.
    :param commit_message:
    :return:
    """
    text = commit_message.message

    commit_message.is_refactor = built_is_refactor(text)
    commit_message.refactor_in_text = re.findall(build_refactor_regex(), text)
    valid_num = len(commit_message.refactor_in_text)
    commit_message.refactor_regex_count = valid_num

    return commit_message

def save_maintenance_activities_log(file_name, data):
    """
    Save the maintenance activities log to a file.
    :param file_name:
    :param data:
    :return:
    """
    path_file = file_name

    opened_file = open(os.path.join(BASE_LOG_MAINTENANCE_ACTIVITIES, path_file), "w+", encoding="latin-1")
    file_contents = ""
    for line in data:
        file_contents += str(line.id) + ";"  # A
        file_contents += str(line.message) + ";"  # B
        file_contents += str(line.bug_fix_regex_count) + ";"  # C
        file_contents += str(line.adaptive_regex_count) + ";"  # D
        file_contents += str(line.adaptive_by_negation_regex_count) + ";"  # E
        file_contents += str(line.perfective_regex_count) + ";"  # F
        file_contents += str(line.refactor_regex_count) + ";"  # G
        file_contents += str(line.is_perfective) + ";"  # H
        file_contents += str(line.is_refactor) + ";"  # I
        file_contents += str(line.is_adaptive) + ";"  # J
        file_contents += str(line.is_adaptive_by_negation) + ";"  # K
        file_contents += str(line.is_corrective) + ";"  # L
        file_contents += str(line.perfective_in_text) + ";"  # M
        file_contents += str(line.refactor_in_text) + ";"  # N
        file_contents += str(line.adaptive_in_text) + ";"  # O
        file_contents += str(line.adaptive_by_negation_in_text) + ";"  # P
        file_contents += str(line.corrective_in_text) + ";"  # Q
        file_contents += "\n"

    opened_file.write("{}".format(file_contents))
    opened_file.close()


def get_maintenance_activities_repo(project_result, db):
    """
    Get the maintenance activities from the repository.
    :param project_result:
    :param db:
    :return:
    """
    logger.info("{now} : BEGIN get_data_repo {base_git_path} \n".format(now=datetime.now(),
                                                                  base_git_path=str(project_result.id)))

    result_repo_test = check_maintenance_activities(db, project_result.id)

    logger.info("{now} : END get_data_repo {base_git_path}\n".format(now=datetime.now(), base_git_path=str(project_result.id)))
    return {"n_corrective": result_repo_test[0], "n_adaptive": result_repo_test[1], "n_perfective": result_repo_test[2],
            "n_multi": result_repo_test[3]}


def check_maintenance_activities(db, pipeline_id):
    """
    Check the maintenance activities in the database.
    :param db:
    :param pipeline_id:
    :return:
    """
    list_maintenance = [0, 0, 0, 0, 0]  # 0- corrective, 1 - adaptive, 2 -perfective, 3- multi

    commit_message_itens = crud.get_commit_message_items_by_pipeline(db, pipeline_id)

    for item in commit_message_itens:
        corrective = 0
        adaptive = 0
        perfective = 0

        if item.is_corrective:
            corrective = 1

        if int(item.is_adaptive) > 0 or item.is_adaptive_by_negation == True:
            adaptive = 1

        if item.is_perfective:
            perfective = 1

        list_maintenance[0] = list_maintenance[0] + corrective
        list_maintenance[1] = list_maintenance[1] + adaptive
        list_maintenance[2] = list_maintenance[2] + perfective

        total = corrective + adaptive + perfective

        if total > 1:
            list_maintenance[3] = list_maintenance[3] + 1

    return list_maintenance