import datetime


class S3Parser:

    @staticmethod
    def compose_path(prefix: str = None, filename: str = None, date_sep: bool = True, file_format: str = 'json',
                     partition: int = 0, datetime_group: datetime = None):

        if not prefix or not filename:
            raise ValueError('Prefix and filename should be specified.')

        now = datetime.datetime.utcnow()

        if partition > 0:
            if datetime_group is None:
                raise ValueError('datetime_group must be specified if partition is set.')

            now = datetime_group

        if date_sep:
            res = '{}/{}'.format(prefix, now.strftime("%Y/%m/%d"))
        else:
            res = '{}'.format(prefix)

        if partition > 0:
            return '{}/{}-{}.{}.{}'.format(res, filename, now, partition, file_format)

        return '{}/{}-{}.{}'.format(res, filename, now, file_format)
