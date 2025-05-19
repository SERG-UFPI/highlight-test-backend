import json
import os
from datetime import datetime

from app.logger_config import logger


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

def get_comma_separated_names(my_list, len_prev, indice_start, pos_start):
    """
    Get a comma-separated string from a list.
    :param my_list:
    :param len_prev:
    :param indice_start:
    :param pos_start:
    :return:
    """
    stop = (pos_start + (len(my_list) - len_prev))
    return ','.join(my_list[indice_start:stop])

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

def is_windows():
    """
    Check if the operating system is Windows.
    :return:
    """
    return os.system("ver") == 0


def parse_int(value:str):
    """
    Parse a string to an integer. If parsing fails, return 0.
    :param value:
    :return:
    """
    try:
        return int(value)
    except ValueError:
        print("Invalid input. Please enter an integer.")
        return 0

def div_safe(num1, num2):
    """
    Perform safe division. If the divisor is zero, return 0.
    :param num1:
    :param num2:
    :return:
    """
    if num2 == 0:
        return 0
    else:
        return num1 / num2

def get_index(array, item):
    """
    Get the index of an item in an array. If not found, return -1.
    :param array:
    :param item:
    :return:
    """
    try:
        return array.index(item)
    except ValueError:
        return -1

def is_valid_date(date_string, date_format="%Y-%m-%d %H:%M:%S"):
    """
    Check if the date string is valid according to the given format.
    :param date_string:
    :param date_format:
    :return:
    """
    try:
        datetime.strptime(date_string, date_format)
        return True
    except ValueError:
        return False

def is_zero_or_one(value: str) -> bool:
    """
    Check if the input string is '0' or '1'.
    :param value: The input string to check.
    :return: True if the string is '0' or '1', otherwise False.
    """
    return value.replace('\n', '') in {"0", "1"}