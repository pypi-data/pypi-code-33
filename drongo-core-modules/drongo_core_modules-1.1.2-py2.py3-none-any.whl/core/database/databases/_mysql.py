import pymysql
import pymysql.cursors

DEFAULT_HOST = 'localhost'
DEFAULT_PORT = 3306
DEFAULT_CHARSET = 'utf8'


class MysqlDatabase(object):
    def __init__(self, app, config):
        host = config.get('host', DEFAULT_HOST)
        port = config.get('port', DEFAULT_PORT)
        user = config.get('user')
        password = config.get('password')
        name = config.get('name')
        charset = config.get('charset', DEFAULT_CHARSET)

        self.connection = pymysql.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            db=name,
            charset=charset,
            cursorclass=pymysql.cursors.DictCursor
        )

    def get(self):
        return self.connection
