import json
import os

def is_empty(path):
    """
    Check if a directory is empty.
    :param path:
    :return:
    """
    dirs = os.listdir( path )

    if len(dirs) == 0 :
        return True

    return False

def clean_create_dir(dir):
    """
    Clean and create a directory.
    :param dir:
    :return:
    """
    if os.path.exists(dir):
      os.system("rm -rf {my_directory}".format(my_directory=dir))

    os.mkdir(dir)

def get_json(dir):
    """
    Get JSON data from a file.
    :param dir:
    :return:
    """
    if os.path.exists(dir):
        with open(dir) as json_file:
            return json.load(json_file)
    return False

def save_json(dir, repository_id, data):
    """
    Save JSON data to a file.
    :param dir:
    :param repository_id:
    :param data:
    :return:
    """
    file_path = dir + repository_id + ".json"
    with open(file_path, 'w') as outfile:
      json.dump(data, outfile)

def save_csv(dir, project_result_id, conteudo):
    """
    Save CSV data to a file.
    :param dir:
    :param project_result_id:
    :param conteudo:
    :return:
    """
    f = open(os.path.join(dir, project_result_id + ".csv"), "w+", encoding="utf-8")
    f.write("{}\r\n".format(conteudo))
    f.close()

def get_comma_separated_names(list, len_prev, indice_start, pos_start):
    """
    Get a comma-separated string from a list.
    :param list:
    :param len_prev:
    :param indice_start:
    :param pos_start:
    :return:
    """
    stop = (pos_start + (len(list) - len_prev))
    return ','.join(list[indice_start:stop])

def create_default_diretories(directories):
    """
    Create default directories if they do not exist.
    :param directories:
    :return:
    """
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"Directory created: {directory}")
        else:
            print(f"Directory already exists: {directory}")

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
