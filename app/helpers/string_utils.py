from app.constants import IMPORTED_PROJECTS_FOLDER_NAME

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

def get_simple_name_path(file_path, uses_external_id, pipeline_id):
    """
    Get the simple name path from the file path.
    :param file_path:
    :param uses_external_id:
    :param pipeline_id:
    :return:
    """
    normalized_path = file_path.replace('\\', '/').replace('//', '/')
    if uses_external_id:
        return normalized_path.rpartition(IMPORTED_PROJECTS_FOLDER_NAME + "/")[-1]
    return normalized_path.rpartition(str(pipeline_id) + "/")[-1]