# The general functions from the utils.py


def check_params_for_board_update(*args, arg_type=str):
    """
        Check if arguments exist and equal to arg_type

        :param args: arguments to check
        :param arg_type: type to check
        :return: True or False
        :rtype: bool
    """
    return all(args) and all(isinstance(x, arg_type) for x in args)
