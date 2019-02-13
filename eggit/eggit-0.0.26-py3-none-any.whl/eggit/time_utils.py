import time
from datetime import datetime


class DTFormat(object):
    '''
    It means DatetimeFormat.
    Provide some date format strings,
    such as::

        >>> from eggit.time_utils import DTFormat
        >>> DTFormat.date_format
        >>> '%Y-%m-%d'
        >>> DTFormat.datetime_format
        >>> '%Y-%m-%d %H:%M:%S'
    '''

    date_format = '%Y-%m-%d'
    datetime_format = '%Y-%m-%d %H:%M:%S'


class DateTimeUtils():
    '''
    Datetime handler.
    '''

    @staticmethod
    def datetime_str_to_timestamp(datetime_str):
        '''
        '2018-01-01 00:00:00' (str) --> 1514736000

        :param str datetime_str: datetime string
        :return: unix timestamp (int) or None
        :rtype: int or None
        '''

        try:
            dtf = DTFormat()
            struct_time = time.strptime(datetime_str, dtf.datetime_format)
            return time.mktime(struct_time)
        except:
            return None

    @staticmethod
    def get_datetime_object(datetime_str):
        '''
        Get datetime object from datetime string

        example:
            DateTimeUtils.get_datetime_object('2018-01-01 00:00:00')

        :param str string: datetime string
        :return: datetime object
        :rtype: datetime
        '''

        try:
            dft = DTFormat()
            return datetime.strptime(datetime_str, dft.datetime_format)
        except:
            return None

    @staticmethod
    def get_datetime_string(datetime_obj):
        '''
        Get datetime string from datetime object

        :param datetime datetime_obj: datetime object
        :return: datetime string
        :rtype: str
        '''

        if isinstance(datetime_obj, datetime):
            dft = DTFormat()
            return datetime_obj.strftime(dft.datetime_format)

        return None

    @staticmethod
    def now_str():
        '''
        Get now datetime str like '2018-01-01 00:00:00' (str)

        :return: datetime string
        :rtype: str
        '''

        dft = DTFormat()
        return datetime.now().strftime(dft.datetime_format)

    @staticmethod
    def timestamp_to_datetime(timestamp):
        '''
        1514736000 --> datetime object

        :param int timestamp: unix timestamp (int)
        :return: datetime object or None
        :rtype: datetime or None
        '''

        if isinstance(timestamp, (int, float, str)):
            try:
                timestamp = float(timestamp)
                if timestamp.is_integer():
                    timestamp = int(timestamp)
            except:
                return None

            temp = str(timestamp).split('.')[0]
            if len(temp) == 13:
                timestamp = timestamp / 1000.0

            if len(temp) < 10:
                return None

        else:
            return None

        return datetime.fromtimestamp(timestamp)

    @staticmethod
    def timestamp_to_datetime_str(timestamp):
        '''
        1514736000 --> '2018-01-01 00:00:00' (str)

        :param int timestamp: unix timestamp
        :return: datetime str
        :rtype: str
        '''

        return DateTimeUtils.get_datetime_string(DateTimeUtils.timestamp_to_datetime(timestamp))
