class Converter(object):
    '''
    Converters will help you convert A type data to B type data.
    '''

    @staticmethod
    def str_to_int(str_val):
        '''
        Convert string to int::

            >>> from eggit.converters import Converter
            >>> result = Converter.str_to_int('123')
            >>> print(result)
            123
            >>> result = Converter.str_to_int('abc')
            >>> print(result)
            None
            >>> result = Converter.str_to_int('1.2')
            >>> print(result)
            None

        :param str str_val: the string value
        :return: the target integer value
        :rtype: int or None
        '''

        try:
            return int(str_val)
        except ValueError:
            return None

    @staticmethod
    def str_to_bool(str_val):
        '''
        Convert string to boolean::

            >>> from eggit.converters import Converter
            >>> Converter.str_to_bool('True')  # or true
            True
            >>> Converter.str_to_bool('False')  # or false
            False
            >>> Converter.str_to_bool('OtherString')
            False

        :param str_val: the source string value
        :return: the target boolean value
        :rtype: bool
        '''
        if (str_val.lower() == 'true'):
            return True

        return False
