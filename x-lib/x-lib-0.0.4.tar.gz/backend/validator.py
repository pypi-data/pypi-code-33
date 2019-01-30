import re

from .exception import ValidationException, CoreException
from .string_utils import is_empty, is_not_digit, is_blank

MESSAGE_UNKNOWN_OBJECT = "unknown object"
MESSAGE_INPUT_MUST_DICT = "input {} must be dict"
MESSAGE_INPUT_INVALID_KEY = "key with name '{}' is required"
MESSAGE_INPUT_INVALID_NOT_EMPTY = "{} must be not empty"
MESSAGE_INPUT_INVALID_NOT_BLANK = "{} must be not blank"
MESSAGE_INPUT_INVALID_NOT_NUMBER = "{} must be number"
MESSAGE_INPUT_INVALID_EMAIL = "Invalid email address"
MESSAGE_INPUT_INVALID_PHONE = "Invalid phone number"
MESSAGE_INPUT_INVALID_SIZE = "{} must be between {} and {}"


class Key(object):
    def __init__(self, keys: list):
        self.keys = keys

    def __call__(self, original_function):
        def new_function(other, input_dict):
            if not isinstance(input_dict, dict):
                raise TypeError(MESSAGE_INPUT_MUST_DICT.format(str(input_dict)))
            for key in self.keys:
                if '.' in key:
                    split = key.split('.')
                    if split[0] not in input_dict:
                        raise ValidationException(MESSAGE_INPUT_INVALID_KEY.format(split[0]), key=split[0])
                    if isinstance(input_dict[split[0]], list):
                        for k in split[1:]:
                            for i, d in enumerate(input_dict[split[0]]):
                                if k not in d:
                                    raise ValidationException(MESSAGE_INPUT_INVALID_KEY.format(k),
                                                              key='{}[{}]'.format(k, i))
                    elif isinstance(input_dict[split[0]], dict):
                        for k in split[1:]:
                            if k not in input_dict[split[0]]:
                                raise ValidationException(MESSAGE_INPUT_INVALID_KEY.format(k), key=k)
                    else:
                        raise TypeError(MESSAGE_UNKNOWN_OBJECT)
                else:
                    if key not in input_dict:
                        raise ValidationException(MESSAGE_INPUT_INVALID_KEY.format(key), key=key)
            return original_function(other, input_dict)

        return new_function


class NotEmpty(object):
    def __init__(self, keys: list):
        self.keys = keys

    def __call__(self, original_function):
        @Key(self.keys)
        def new_function(other, input_dict):
            for key in self.keys:
                if '.' in key:
                    split = key.split('.')
                    if isinstance(input_dict[split[0]], list):
                        for k in split[1:]:
                            for i, d in enumerate(input_dict[split[0]]):
                                if is_empty(d[k]):
                                    raise ValidationException(MESSAGE_INPUT_INVALID_NOT_EMPTY.format(k),
                                                              key='{}[{}]'.format(k, i))
                    elif isinstance(input_dict[split[0]], dict):
                        for k in split[1:]:
                            d = input_dict[split[0]]
                            for k1 in d:
                                if is_empty(d[k1]):
                                    raise ValidationException(MESSAGE_INPUT_INVALID_NOT_EMPTY.format(k),
                                                              key='{}'.format(k))
                    else:
                        raise TypeError(MESSAGE_UNKNOWN_OBJECT)
                else:
                    if is_empty(input_dict[key]):
                        raise ValidationException(MESSAGE_INPUT_INVALID_NOT_EMPTY.format(k), key=key)
            return original_function(other, input_dict)

        return new_function


class NotBlank(object):
    def __init__(self, keys: list):
        self.keys = keys
        pass

    def __call__(self, original_function):
        @Key(self.keys)
        def new_function(other, input_dict):
            for key in self.keys:
                if '.' in key:
                    split = key.split('.')
                    if isinstance(input_dict[split[0]], list):
                        for k in split[1:]:
                            for i, d in enumerate(input_dict[split[0]]):
                                if is_blank(d[k]):
                                    raise ValidationException(MESSAGE_INPUT_INVALID_NOT_BLANK.format(k),
                                                              key='{}[{}]'.format(k, i))
                    elif isinstance(input_dict[split[0]], dict):
                        for k in split[1:]:
                            d = input_dict[split[0]]
                            for k1 in d:
                                if is_blank(d[k1]):
                                    raise ValidationException(MESSAGE_INPUT_INVALID_NOT_BLANK.format(k), key=k)
                    else:
                        raise TypeError(MESSAGE_UNKNOWN_OBJECT)
                else:
                    if is_blank(input_dict[key]):
                        raise ValidationException(MESSAGE_INPUT_INVALID_NOT_BLANK.format(key), key=key)
            return original_function(other, input_dict)

        return new_function


class Number(object):
    def __init__(self, keys: list):
        self.keys = keys
        pass

    def __call__(self, original_function):
        @Key(self.keys)
        def new_function(other, input_dict):

            for key in self.keys:
                if '.' in key:
                    split = key.split('.')

                    if isinstance(input_dict[split[0]], list):
                        for k in split[1:]:
                            for i, d in enumerate(input_dict[split[0]]):
                                if is_not_digit(d[k]):
                                    raise ValidationException(MESSAGE_INPUT_INVALID_NOT_NUMBER.format(k),
                                                              key='{}[{}]'.format(k, i))
                    elif isinstance(input_dict[split[0]], dict):
                        for k in split[1:]:
                            d = input_dict[split[0]]
                            for k1 in d:
                                if is_not_digit(d[k1]):
                                    raise ValidationException(MESSAGE_INPUT_INVALID_NOT_NUMBER.format(k),
                                                              key='{}'.format(k))
                    else:
                        raise TypeError(MESSAGE_UNKNOWN_OBJECT)
                else:
                    if is_not_digit(str(input_dict[key])):
                        raise ValidationException(MESSAGE_INPUT_INVALID_NOT_NUMBER.format(key), key=key)
            return original_function(other, input_dict)

        return new_function


class Email(object):

    def __init__(self, keys: list):
        self.keys = keys
        self.mail_re = r"^[_A-Za-z0-9-\+]+(\.[_A-Za-z0-9-]+)*@[A-Za-z0-9-]+(\.[A-Za-z0-9]+)*(\.[A-Za-z]{2,})$"
        pass

    def __call__(self, original_function):
        @Key(self.keys)
        def new_function(other, input_dict):
            for key in self.keys:
                if '.' in key:
                    split = key.split('.')
                    if isinstance(input_dict[split[0]], list):
                        for k in split[1:]:
                            for i, d in enumerate(input_dict[split[0]]):
                                if not bool(re.match(self.mail_re, d[k])):
                                    raise ValidationException(MESSAGE_INPUT_INVALID_EMAIL, key='{}[{}]'.format(k, i))
                    elif isinstance(input_dict[split[0]], dict):
                        for k in split[1:]:
                            d = input_dict[split[0]]
                            for k1 in d:
                                if not bool(re.match(self.mail_re, d[k1])):
                                    raise ValidationException(MESSAGE_INPUT_INVALID_EMAIL, key='{}'.format(k))
                    else:
                        raise TypeError(MESSAGE_UNKNOWN_OBJECT)
                else:
                    if not bool(re.match(self.mail_re, input_dict[key])):
                        raise ValidationException(MESSAGE_INPUT_INVALID_EMAIL, key=key)
            return original_function(other, input_dict)

        return new_function


class Phone(object):
    def __init__(self, keys: list):
        self.keys = keys
        self.phone_re = r"(\+[0-9]+[\- \.]*)?(\([0-9]+\)[\- \.]*)?([0-9][0-9\-\.]+[0-9])"
        pass

    def __call__(self, original_function):
        @Key(self.keys)
        def new_function(other, input_dict: dict):
            for key in self.keys:
                if '.' in key:
                    split = key.split('.')
                    if isinstance(input_dict[split[0]], list):
                        for k in split[1:]:
                            for i, d in enumerate(input_dict[split[0]]):
                                if not bool(re.match(self.phone_re, d[k])):
                                    raise ValidationException(MESSAGE_INPUT_INVALID_PHONE,
                                                              key='{}[{}]'.format(k, i))
                    elif isinstance(input_dict[split[0]], dict):
                        for k in split[1:]:
                            d = input_dict[split[0]]
                            for k1 in d:
                                if not bool(re.match(self.phone_re, d[k1])):
                                    raise ValidationException(MESSAGE_INPUT_INVALID_PHONE, key=k)
                    else:
                        raise CoreException(MESSAGE_UNKNOWN_OBJECT)
                else:
                    if not bool(re.match(self.phone_re, input_dict[key])):
                        raise ValidationException(MESSAGE_INPUT_INVALID_PHONE, key=key)
            return original_function(other, input_dict)

        return new_function


class Size(object):
    def __init__(self, keys: list, minimum=0, maximum: int = 10):
        self.keys = keys
        self.min = minimum
        self.max = maximum
        pass

    def __call__(self, original_function):

        @Key(self.keys)
        def new_function(other, input_dict):
            if self.min >= self.max:
                raise TypeError('min {} greater than max {}'.format(self.min, self.max))
            if self.max <= self.min:
                raise TypeError('max {} less than min {}'.format(self.min, self.max))
            for key in self.keys:
                if '.' in key:
                    split = key.split('.')
                    if isinstance(input_dict[split[0]], list):
                        for k in split[1:]:
                            for i, d in enumerate(input_dict[split[0]]):
                                if not self.min <= len(d[k]) <= self.max:
                                    raise ValidationException(MESSAGE_INPUT_INVALID_SIZE.format(k, self.min, self.max),
                                                              key='{}[{}]'.format(k, i))
                    elif isinstance(input_dict[split[0]], dict):
                        for k in split[1:]:
                            d = input_dict[split[0]]
                            for k1 in d:
                                if not self.min <= len(d[k1]) <= self.max:
                                    raise ValidationException(MESSAGE_INPUT_INVALID_SIZE.format(k1, self.min, self.max), key=k)
                    else:
                        raise CoreException(MESSAGE_UNKNOWN_OBJECT)
                else:
                    if not self.min <= len(input_dict[key]) <= self.max:
                        raise ValidationException(MESSAGE_INPUT_INVALID_SIZE.format(key, self.min, self.max), key=key)
            return original_function(other, input_dict)

        return new_function
