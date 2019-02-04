"""
jt-py-first-package Python package is for Joe Tilsed to learn how to write a python package and
upload it onto PyPi. Also to show and teach others how to do it themselves.
"""

name = "jt-py-first-package"


def hello_world():
    """
    Gain the string "Hello World"
    :return:
    "Hello World"
    """
    return "Hello World!"


def hello_user(user):
    """
    Gain the string "Hello <user>" where <user> is what was passed in param
    :param user:
    The users name
    :return:
    "Hello <user>" where <user> is what was passed in param
    """
    return "Hello {}".format(user)


# That's all folks...
