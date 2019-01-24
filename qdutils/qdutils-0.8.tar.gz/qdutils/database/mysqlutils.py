#  -*- coding: utf-8 -*-

'''

@desc: mysql工具类
@author: tony
@Date: 2018/12/27 下午4:03

'''
import base64
import MySQLdb
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy import create_engine
from qdutils.common.stringutils import stringutils


class mysqlutils(object):
    pass
    FORMAT_STRING = '##'
    # cursors
    CURSOR_MODE = 0
    DICTCURSOR_MODE = 1
    SSCURSOR_MODE = 2
    SSDICTCURSOR_MODE = 3

    # sqlalchemy
    POOL_SIZE = 30
    MAX_OVERFLOW = 30
    POOL_RECYCLE = 30
    ECHO = True
    conn_common = 'mysql+mysqldb://{}:{}@{}:{}/{}?charset=utf8'
    # 连接引擎dict，key：连接实例串，value：连接engine
    conn_engine_dict = {}

    class EngineObj(object):
        engine = None
        create_time = None
        recent_use_time = None
        conn_num = None

        def __init__(self, engine, create_time, recent_use_time=None, conn_num=0):
            self.engine = engine
            self.create_time = create_time
            self.recent_use_time = recent_use_time
            self.conn_num = conn_num

    def get_conn(self, host, port, user, passwd, db_name):
        """
        获取数据库连接实例
        :param host:    连接host
        :param port:    端口 
        :param user:    账号 
        :param passwd:  密码 
        :param db_name: 数据库名 
        :return: 数据库连接实例
        """
        conn = None
        conn = MySQLdb.connect(host=host,
                               port=int(port),
                               user=user,
                               passwd=passwd,
                               db=db_name, charset='utf8')
        return conn

    def get_cur(self, host, port, user, passwd, db_name, mode=CURSOR_MODE):
        """
        获取数据库连接光标
        :param host:    连接host
        :param port:    端口 
        :param user:    账号 
        :param passwd:  密码 
        :param db_name: 数据库名  
        :param mode:    数据库 
        :return:    连接光标 
        """
        if mode == self.CURSOR_MODE:
            curclass = MySQLdb.cursors.Cursor
        elif mode == self.DICTCURSOR_MODE:
            curclass = MySQLdb.cursors.DictCursor
        elif mode == self.SSCURSOR_MODE:
            curclass = MySQLdb.cursors.SSCursor
        elif mode == self.SSDICTCURSOR_MODE:
            curclass = MySQLdb.cursors.SSDictCursor
        else:
            raise Exception("mode value is wrong")
        conn = self.get_conn(host, port, user, passwd, db_name)
        return conn.cursor(cursorclass=curclass)

    def get_conn_cur(self, conn, mode=CURSOR_MODE):
        """
        获取数据库连接光标
        :param conn: 连接实例  
        :param mode:    数据库 
        :return:    连接光标 
        """
        if mode == self.CURSOR_MODE:
            curclass = MySQLdb.cursors.Cursor
        elif mode == self.DICTCURSOR_MODE:
            curclass = MySQLdb.cursors.DictCursor
        elif mode == self.SSCURSOR_MODE:
            curclass = MySQLdb.cursors.SSCursor
        elif mode == self.SSDICTCURSOR_MODE:
            curclass = MySQLdb.cursors.SSDictCursor
        else:
            raise Exception("mode value is wrong")
        return conn.cursor(cursorclass=curclass)

    @staticmethod
    def create_engine(conn_string, set_pool_size=POOL_SIZE, set_max_overflow=MAX_OVERFLOW,
                      set_pool_recycle=POOL_RECYCLE,
                      set_echo=ECHO):
        """
        :param conn_string: 连接串
        :param set_pool_size: 
        :param set_max_overflow: 
        :param set_pool_recycle: 
        :param set_echo: 
        :return: 连接引擎
        """
        engine = create_engine(
            conn_string, pool_size=set_pool_size, max_overflow=set_max_overflow, pool_recycle=set_pool_recycle,
            echo=set_echo)
        return engine

    @staticmethod
    def create_engine_string(host, port, user, passwd, db_name, is_base64=False):
        """
        创建mysql engine
        :param host:    连接host
        :param port:    端口 
        :param user:    账号 
        :param passwd:  密码 
        :param db_name: 数据库名 
        :param is_base64:密码是否已base64处理 
        :return: 
        """
        if is_base64:
            set_passwd = base64.b64decode(passwd)
        else:
            set_passwd = base64.b64decode(passwd)
        engine_string = mysqlutils.conn_common.format(user, set_passwd, host, port, db_name)
        return engine_string

    @staticmethod
    def __get_engine_key(host, port, user, passwd, db_name):
        format_str = mysqlutils.FORMAT_STRING
        engine_key = '{}{}{}{}{}{}{}{}'.format(host, format_str, port, format_str, user, format_str, passwd, format_str,
                                               db_name)
        engine_key = stringutils.md5(engine_key)
        return engine_key

    @staticmethod
    def get_session_sqlalchemy(host, port, user, passwd, db_name, autocommit=True, autoflush=True, is_base64=False):
        """
        获取数据库连接会话
        :param host:    连接host
        :param port:    端口 
        :param user:    账号 
        :param passwd:  密码 
        :param db_name: 数据库名  
        :param autocommit:是否自动提交事务 
        :param autoflush: 是否自动刷写 
        :param is_base64: 密码是否已base64处理
        :return: 连接会话
        """
        engine_string = mysqlutils.create_engine_string(host, port, user, passwd, db_name, is_base64)
        engine = mysqlutils.create_engine(engine_string)
        session_factory = sessionmaker(autocommit=autocommit,
                                       autoflush=autoflush, bind=engine)
        session = scoped_session(session_factory)
        return session

    @staticmethod
    def get_session_mem_engine(host, port, user, passwd, db_name, autocommit=True, autoflush=True, is_base64=False):
        """
        获取数据库连接会话
        :param host:    连接host
        :param port:    端口 
        :param user:    账号 
        :param passwd:  密码 
        :param db_name: 数据库名  
        :param autocommit:是否自动提交事务 
        :param autoflush: 是否自动刷写 
        :param is_base64: 密码是否已base64处理
        :return: 连接会话
        """
        engine_key = mysqlutils.__get_engine_key(host, port, user, passwd, db_name)
        engine = None
        if mysqlutils.conn_engine_dict.has_key(engine_key):
            pass
        else:
            engine_string = mysqlutils.create_engine_string(host, port, user, passwd, db_name, is_base64)
            engine = mysqlutils.create_engine(engine_string)
        session_factory = sessionmaker(autocommit=autocommit,
                                       autoflush=autoflush, bind=engine)
        session = scoped_session(session_factory)
        return session

    @staticmethod
    def get_session_by_engine(engine, autocommit=True, autoflush=True):
        """
        获取数据库连接会话
        :param engine: 连接引擎  
        :param autocommit:是否自动提交事务 
        :param autoflush: 是否自动刷写 
        :param is_base64: 密码是否已base64处理
        :return: session: 连接会话
        """
        session_factory = sessionmaker(autocommit=autocommit,
                                       autoflush=autoflush, bind=engine)
        session = scoped_session(session_factory)
        return session
