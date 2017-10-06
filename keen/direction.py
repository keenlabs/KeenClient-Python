# Helper file for avoiding string literals prone to typos with order_by.

ASCENDING = "ASC"
DESCENDING = "DESC"

def is_valid_direction(direction_string):
    """
    Determines whether the given string is a valid direction string
    for order_by.

    :param direction_string: A string representing an order_by direction.
    :return: True if the string is a valid direction string, False otherwise.
    """
    return direction_string in [ASCENDING, DESCENDING]
