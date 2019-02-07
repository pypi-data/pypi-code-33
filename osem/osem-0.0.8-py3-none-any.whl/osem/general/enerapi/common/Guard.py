class Guard(object):
    """docstring for Guard functions"""

    @staticmethod
    def check_if_key_in_dict(dict_key, keys_in_dict):
        if dict_key not in keys_in_dict.keys():
            raise DomainException("Missing parameter '{0}'".format(dict_key))

    @staticmethod
    def check_if_value_in_list(value, **kwargs):
        if value not in kwargs['values']:
            raise DomainException("'{0}' is not supported".format(value))

    @staticmethod
    def check_value_in_between(value, **kwargs):
        if 'max' in kwargs.keys() and 'min' in kwargs.keys() and kwargs['max'] >= kwargs['min']:
            if 'max_in' in kwargs.keys() and not kwargs['max_in']:
                Guard.check_is_higher(kwargs['max'], lower_limit=value, strict=True)

            if 'min_in' in kwargs.keys() and not kwargs['min_in']:
                Guard.check_is_higher(value, lower_limit=kwargs['min'], strict=True)

            Guard.check_is_higher(value, lower_limit=kwargs['min'])
            Guard.check_is_higher(kwargs['max'], lower_limit=value)
        else:
            raise DomainException("WRONG REQUEST FOR CHECK_VALUE_IN_BETWEEN")

    @staticmethod
    def check_is_higher(value, **kwargs):

        if 'strict' in kwargs.keys() and kwargs['strict']:
            if value <= kwargs['lower_limit']:
                raise DomainException("Found '{}', but value must be STRICTLY higher than '{}'".
                                      format(value, kwargs['lower_limit']))
        else:
            if value < kwargs['lower_limit']:
                raise DomainException("Found '{}', but value must be higher than '{}'".
                                      format(value, kwargs['lower_limit']))

    @staticmethod
    def check_for_minimum_number_of_value_in_a_list(a_list, **kwargs):
        if len(a_list) < kwargs["min"]:
            raise DomainException("The minimum number of points is {} and not '{}' (with {})"
                                  .format(kwargs["min"], len(a_list), a_list))

    @staticmethod
    def check_for_same_list_lengths(**kwargs):
        len_lists = {}
        for key, val in kwargs.items():
            len_lists[key] = len(val)

        if not len(set(len_lists.values())) == 1:
            error_message = "All lists have to be of the same length:\n"
            for key, val in len_lists.items():
                error_message += "\tList '{}' has a length of '{}'.\n".format(key, val)
            raise DomainException(error_message)

    @staticmethod
    def check_for_every_item_of_list(a_list, check_value, **kwargs):
        for value in a_list:
            check_value(value, **kwargs)

    @staticmethod
    def check_if_list_is_sorted(a_list, **kwargs):
        if "reverse" in kwargs.keys() and kwargs["reverse"]:
            sorted_list = sorted(a_list, reverse=True)
        else:
            sorted_list = sorted(a_list)

        if sorted_list != a_list:
            error_message = "The list is not sorted"
            raise DomainException(error_message)

