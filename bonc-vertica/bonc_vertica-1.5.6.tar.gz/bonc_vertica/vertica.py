"""
脚本说明
本脚本用以从Vertica数据库中导出数据。
读取配置信息后，程序启动一个UI界面，用以接收用户要查询的SQL。点击“确定并导出”程序会连接数据库、查询数据。
如果查询成功，程序会要求一个另存为文件。程序会以CSV格式将数据保存为文本文件。

脚本曾尝试一次性连接、一次性下载全部数据，再写入本地，但查询数据量大时，这样操作会对内存造成较大压力。
因此脚本运行期间，会一直保持与数据库的连接，将查询到的数据逐步写入本地文件。

选择“另存为”文件时，如果文件已经存在，会询问是否替换文件，如果你选择了确定，程序也不会真的替换文件，只会在文件后追加。

使用脚本须要用到vertica_python库，请pip install vertica-python安装

后续迭代：
当前版本尚只支持UTF8编码格式导出，后续会尝试其他编码格式。
查询数据量过大时，文件会很大，后续版本会考虑设置最大单文件行数，当超出最大行数后，会新建文件写入。
"""
import sys
import vertica_python

from bonc_vertica.settings import logging


__auth__ = 'chenzhongrun'
__mail__ = 'chenzhongrun@bonc.com.cn'
__version__ = '1.0'


class Selection(object):
    """
    负责启动数据库连接、关闭数据连接、查询数据
    """
    def __init__(self, conn_info):
        self.conn_info = conn_info

    def select(self, sql):
        """
        调用Vertica的Python驱动，查询数据，避免内存占用过大，返回一个迭代器
        """
        try:
            result = self.cur.execute(sql).iterate()
            # result = self.cur.execute(sql).fetchall()
            return result
        except vertica_python.errors.Error as e:
            logging.error('查询失败。失败原因如下，请联系{}或重试'.format(__mail__))
            raise e

    def __enter__(self):
        try:
            self.conn = vertica_python.connect(**self.conn_info)
            self.cur = self.conn.cursor()
        except vertica_python.errors.ConnectionError as e:
            logging.error('连接失败。失败原因如下，请联系{}或重试'.format(__mail__))
            raise e
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.close()

