import os

def is_windows():
    """
    Check if the operating system is Windows.
    :return:
    """
    return os.system("ver") == 0