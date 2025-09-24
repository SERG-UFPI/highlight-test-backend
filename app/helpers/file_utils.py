import json
import os
from ..logger_config import logger

def is_empty(path):
    """
    Check if a directory is empty.
    :param path:
    :return:
    """
    dirs = os.listdir(path)

    if len(dirs) == 0 :
        return True

    return False

def clean_create_dir(my_directory):
    """
    Clean and create a directory.
    :param my_directory:
    :return:
    """
    if os.path.exists(my_directory):
      os.system("rm -rf {my_directory}".format(my_directory=my_directory))

    os.mkdir(my_directory)

def get_json(my_directory):
    """
    Get JSON data from a file.
    :param my_directory:
    :return:
    """
    if os.path.exists(my_directory):
        with open(my_directory) as json_file:
            return json.load(json_file)
    return False

def save_json(my_directory, repository_id, data):
    """
    Save JSON data to a file.
    :param my_directory:
    :param repository_id:
    :param data:
    :return:
    """
    file_path = my_directory + repository_id + ".json"
    with open(file_path, 'w') as outfile:
      json.dump(data, outfile)

def save_csv(my_directory, project_result_id, conteudo):
    """
    Save CSV data to a file.
    :param my_directory:
    :param project_result_id:
    :param conteudo:
    :return:
    """
    f = open(os.path.join(my_directory, project_result_id + ".csv"), "w+", encoding="utf-8")
    f.write("{}\r\n".format(conteudo))
    f.close()

def create_default_diretories(directories):
    """
    Create default directories if they do not exist.
    :param directories:
    :return:
    """
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            logger.info(f"Directory created: {directory}")
        else:
            logger.info(f"Directory already exists: {directory}")