

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





