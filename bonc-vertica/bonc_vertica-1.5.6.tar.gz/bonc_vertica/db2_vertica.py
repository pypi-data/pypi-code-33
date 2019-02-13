import io
import csv
import copy

try:
    import ibm_db
except ImportError:
    print('请确定已安装ibm-db，如未安装，请使用pip install ibm-db')
    sys.exit(0)
import vertica_python

from bonc_vertica.settings import account_dict, db2_account_dict, conn_info as vertica_conn_info, logging


class DB2Selector(object):
    def __init__(self, encoding, newline='\n', delimiter=','):
        self._connect_info = None
        self._connection = None
        self.sql = None
        self._newline = newline
        self._delimiter = delimiter
        self._encoding = encoding

    def connect(self, connect_info):
        self._connect_info = connect_info
        self._connection = ibm_db.connect(
            self._connect_info,
            '',
            ''
        )

    def select(self, sql):
        """
        select data from db2 and yield row
        :param sql:
        :return:
        """
        self.sql = sql
        logging.info('now is executing SQL: {}'.format(self.sql))
        select_result = ibm_db.exec_immediate(self._connection, self.sql)
        one_row = ibm_db.fetch_tuple(select_result)
        while one_row:
            yield one_row
            one_row = ibm_db.fetch_tuple(select_result)


class VerticaLoader(object):
    def __init__(self, table, fields, delimiter=','):
        self._connect_info = None
        self._connection = None
        self.table = table
        self._fields = fields
        self._delimiter = delimiter

    def connect(self, connect_info):
        self._connect_info = connect_info
        self._connection = vertica_python.connect(**vertica_conn_info)

    def load_data(self, wrapper):
        copy_sql = "COPY {table_name} ({fields}) from stdin delimiter '{delimiter}'".format(
            table_name=self.table,
            fields=self._fields,
            delimiter=self._delimiter,
        )
        logging.info('正在执行导入 SQL: {}'.format(copy_sql))
        cur = self._connection.cursor()
        cur.copy(sql=copy_sql, data=wrapper)


class FromDB2ToVertica(object):
    def __init__(self, db2_conn_info=None, vertica_conn_info=None, db2_sql=None, vertica_table=None, vertica_fields=None,
                 encoding='utf8', delimiter=',', newline='\n'):
        self.db2_selector = DB2Selector(encoding=encoding, newline=newline, delimiter=delimiter)
        self.vertica_loader = VerticaLoader(table=vertica_table, fields=vertica_fields, delimiter=delimiter)
        self.sql = db2_sql
        self.db2_conn_info = db2_conn_info
        self.vertica_conn_info = vertica_conn_info
        self.newline = newline
        self.delimiter = delimiter
        self.encoding = encoding

    def rows_to_wrapper(self, rows):
        """
        vertica的cur.copy(sql, data)方法中，data是一个支持read()方法的类似的文件句柄的对象，
        所以此处把从DB2中下载的数据先转换成句柄对象。
        字段分隔符采用的是英文逗号，尚不明确是否会产生分隔问题。
        :param rows:
        :return:
        """
        lines = self.newline.join([self.delimiter.join(r) for r in rows])
        f_handle = io.BytesIO(bytes(lines, encoding=self.encoding))
        wrapper = io.TextIOWrapper(f_handle, encoding=self.encoding, newline=self.newline)
        return wrapper

    def run(self):
        logging.info('try to connect to db2')
        self.db2_selector.connect(connect_info=self.db2_conn_info)
        logging.info('try to connect to vertica')
        self.vertica_loader.connect(connect_info=self.vertica_conn_info)

        result = self.db2_selector.select(sql=self.sql)
        rows_for_vertica = []
        current_rows_count = 0
        for rows_count, row in enumerate(result, 1):
            if rows_count == 1:
                logging.info('preview the first row')
                print(row)
            if current_rows_count <= 10000:
                current_rows_count += 1
                rows_for_vertica.append(row)
            else:
                current_rows_count = 0
                wrapper = self.rows_to_wrapper(rows=rows_for_vertica)
                self.vertica_loader.load_data(wrapper=wrapper)
                rows_for_vertica = []
        if rows_for_vertica:
            wrapper = self.rows_to_wrapper(rows=rows_for_vertica)
            self.vertica_loader.load_data(wrapper=wrapper)
        logging.info('\n从DB2中查询了{count}行\n向Vertica {tablename} 导入了{count}行'.format(
            tablename=self.vertica_loader.table,
            count=rows_count
        ))

    def db2_to_local(self, to_file):
        self.db2_selector.connect(connect_info=self.db2_conn_info)
        result = self.db2_selector.select(sql=self.sql)
        rows_for_loading = []
        current_rows_count = 0
        for rows_count, row in enumerate(result, 1):
            if rows_count == 1:
                logging.info('preview the first row')
                print(row)
            if current_rows_count <= 10000:
                current_rows_count += 1
                rows_for_loading.append(row)
            else:
                current_rows_count = 0
                with open(to_file, encoding=self.encoding, mode='a+', newline='') as f:
                    f_csv = csv.writer(f)
                    f_csv.writerows(rows_for_loading)
                rows_for_loading = []
        if rows_for_loading:
            with open(to_file, encoding=self.encoding, mode='a+', newline='') as f:
                f_csv = csv.writer(f)
                f_csv.writerows(rows_for_loading)


class SelectAndImport(object):
    def __init__(self, db2_sql, vertica_tablename, select_fields, encoding, delimiter=',', newline='\n'):
        self.db2_sql = db2_sql
        self.vertica_tablename = vertica_tablename
        self.select_fields = ','.join(select_fields) if isinstance(select_fields, list) else select_fields
        self.encoding = encoding
        self.delimiter = delimiter
        self.newline = newline

    @property
    def db2_connection(self):
        return ibm_db.connect(
            'DATABASE=zjdw;HOSTNAME=134.96.33.115;PORT=50012;PROTOCOL=TCPIP;UID=lzdmt03;PWD=L03DMT03',
            '',
            ''
        )

    @property
    def vertica_connection(self):
        return vertica_python.connect(**vertica_conn_info)

    def select_from_db2(self):
        """
        select data from db2 and yield row
        :param sql:
        :return:
        """
        logging.info('now is executing SQL: {}'.format(self.db2_sql))
        select_result = ibm_db.exec_immediate(self.db2_connection, self.db2_sql)
        return select_result

    def import_data_to_vertica(self, wrapper):
        copy_sql = "COPY {table_name} ({fields}) from stdin delimiter '{delimiter}'".format(
            table_name=self.vertica_tablename,
            fields=self.select_fields,
            delimiter=self.delimiter,
        )
        logging.info('正在执行导入 SQL: {}'.format(copy_sql))
        cur = self.vertica_connection.cursor()
        cur.copy(sql=copy_sql, data=wrapper)

    def rows_to_wrapper(self, rows):
        """
        vertica的cur.copy(sql, data)方法中，data是一个支持read()方法的类似的文件句柄的对象，
        所以此处把从DB2中下载的数据先转换成句柄对象。
        字段分隔符采用的是英文逗号，尚不明确是否会产生分隔问题。
        :param rows:
        :return:
        """
        lines = self.newline.join([self.delimiter.join(r) for r in rows])
        f_handle = io.BytesIO(bytes(lines, encoding=self.encoding))
        wrapper = io.TextIOWrapper(f_handle, encoding=self.encoding, newline=self.newline)
        return wrapper

    def run(self):
        ibm_conn = ibm_db.connect(
            'DATABASE=zjdw;HOSTNAME=134.96.33.115;PORT=50012;PROTOCOL=TCPIP;UID=lzdmt03;PWD=L03DMT03',
            '',
            ''
        )
        logging.info('正在执行查询 SQL: {}'.format(self.db2_sql))
        rows_from_db2 = ibm_db.exec_immediate(ibm_conn, self.db2_sql)
        rows_for_vertica = []
        current_rows_count = 0
        rows_count = 0

        one_row = ibm_db.fetch_tuple(rows_from_db2)
        logging.info('单行预览：')
        print(one_row)
        while one_row:
            rows_count += 1
            if current_rows_count < 10000:
                current_rows_count += 1
                rows_for_vertica.append(one_row)
            else:
                wrapper = self.rows_to_wrapper(rows=rows_for_vertica)
                self.import_data_to_vertica(wrapper=wrapper)
                logging.info('向Vertica {} 导入了{}行'.format(self.vertica_tablename, rows_count))
                current_rows_count = 0
                rows_for_vertica = []
            one_row = ibm_db.fetch_tuple(rows_from_db2)

        if rows_for_vertica:
            wrapper = self.rows_to_wrapper(rows=rows_for_vertica)
            self.import_data_to_vertica(wrapper=wrapper)
        logging.info('\n从DB2中查询了{count}行\n向Vertica {tablename} 导入了{count}行'.format(
            tablename=self.vertica_tablename, count=rows_count))
