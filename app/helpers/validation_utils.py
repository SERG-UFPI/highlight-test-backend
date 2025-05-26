from datetime import datetime

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

def parse_bool_safe(value: str) -> bool:
    """
    Parse a string to a boolean. If parsing fails, return False.
    :param value: The input string to parse.
    :return: A boolean value.
    """
    return value.lower() in {"true", "1"}