


class Base(object):
    """
    Base class for most business logic objects.
    Contains utility and setup functions
    """

    _default_parameter_value = {}
    features = None

    def __init__(self, args):
        Base._apply_default(args, self._default_parameter_value)

    @staticmethod
    def _apply_default(args, default_args):
        """
        Updates the given args dictionary with default values when missing.
        :param args: Given arguments
        :param default_args: Default argument values. Typically use self._default_parameter_value
        :return: Nothing
        """
        new_args = args.copy()
        # Start by applying the default values
        for key, value in default_args.items():
            args[key] = default_args[key]
        # Then apply the given argument values
        for key, value in new_args.items():
            args[key] = new_args[key]
