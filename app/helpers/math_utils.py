
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