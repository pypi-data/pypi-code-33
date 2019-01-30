
import re
import logging


class Base(object):
    FORMAT = '%(asctime)-15s %(clientip)s %(user)-8s %(message)s'

    def __init__(self, merchant_id, secret='', **args):
        self.merchant_id = merchant_id
        self.secret = secret

        logging.basicConfig(format=self.FORMAT)
        self.logger = logging.getLogger('a3')


    def validate_phone(self, phone):
        """Validate phone number

        See also: https://en.wikipedia.org/wiki/Telephone_numbers_in_Russia

        >>> Base().validate_phone('9100000000')
        True
        >>> Base().validate_phone('+79100000000')
        True
        >>> Base().validate_phone('89100000000')
        True

        :param phone: str
        :return: bool
        """
        pattern = r"^(\+?7|8)?(9\d{2})(\d{7})$"
        return True if re.compile(pattern).match(phone.replace(' ', '')) else False
