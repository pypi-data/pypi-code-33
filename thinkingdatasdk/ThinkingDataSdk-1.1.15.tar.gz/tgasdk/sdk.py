# encoding:utf-8

from __future__ import unicode_literals
import base64
import datetime
import gzip
import json
import os
import re
import threading
import logging
import logging.handlers
import time

import requests
from requests import ConnectionError

from tgasdk.TGAException import TGAException, TGANetworkException, TGAIllegalDataException

SDK_VERSION = '1.1.14'
try:
    import queue
except ImportError:
    import Queue as queue
try:
    isinstance("", basestring)


    def is_str(s):
        return isinstance(s, basestring)
except NameError:
    def is_str(s):
        return isinstance(s, str)

try:
    isinstance(1, long)


    def is_int(n):
        return isinstance(n, int) or isinstance(n, long)
except NameError:
    def is_int(n):
        return isinstance(n, int)


class TGAnalytics(object):
    """
    TGAnalytics construct

    :param consumer: 数据格式化和传输方式.
    """

    def __init__(self, consumer):
        self.__consumer = consumer
        self.__super_properties = {}
        self.clear_super_properties()
        self.track_pattern = re.compile(r"^(#[a-z][a-z0-9_]{0,49})|([a-z][a-z0-9_]{0,50})$", re.I)
        self.user_pattern = re.compile(r"^(#[a-z][a-z0-9_]{0,49})|([a-z][a-z0-9_]{0,50})$", re.I)

    """
    :param distinct_id: 匿名id
    :param account_id:  注册id
    :param properties:  属性
    """

    def user_set(self, distinct_id=None, account_id=None, properties=None):
        self.__add(distinct_id, account_id, 'user_set', None, properties)

    def user_setOnce(self, distinct_id=None, account_id=None, properties=None):
        self.__add(distinct_id, account_id, 'user_setOnce', None, properties)

    def user_add(self, distinct_id=None, account_id=None, properties=None):
        self.__add(distinct_id, account_id, 'user_add', None, properties)

    def user_del(self, distinct_id=None, account_id=None, properties=None):
        if properties == None:
            properties['#time'] = datetime.datetime.now()
        self.__add(distinct_id, account_id, 'user_del', None, properties)

    def track(self, distinct_id=None, account_id=None, event_name=None, properties=None):
        all_properties = self.__super_properties.copy()
        if properties:
            all_properties.update(properties)
        if not is_str(event_name):
            raise TGAIllegalDataException('Event_name of track is invalid,it must be set a str')

        self.__add(distinct_id, account_id, 'track', event_name, all_properties)

    def flush(self):
        self.__consumer.flush()

    def close(self):
        self.__consumer.close()

    def __add(self, distinct_id, account_id, type, event_name, properties1):
        if properties1:
            properties = properties1.copy()
        else:
            properties = {}
        if distinct_id == None and account_id == None:
            raise TGAException("Distinct_id and account_id must be set at least one")

        self.__assertProperties(type, properties)
        time_event = properties.get("#time",)
        del (properties['#time'])

        ip = properties.get("#ip", "")
        if "#ip" in properties.keys():
            del (properties['#ip'])
        if 'track' == type:
            data = {
                '#time': time_event,
                '#ip': ip,
                '#type': type,
                '#event_name': event_name,
                'properties': properties
            }
        else:
            data = {
                '#time': time_event,
                '#ip': ip,
                '#type': type,
                'properties': properties
            }
        if distinct_id != None:
            data['#distinct_id'] = distinct_id
        if account_id != None:
            data['#account_id'] = account_id

        # self.__consumer.send(str(data))#python3
        self.__consumer.send(json.dumps(data))  # python2

    def __assertProperties(self, action_type, properties):
        key_pattern = self.__getKeyNamePattern(action_type)
        if properties is not None:

            if "#time" not in properties.keys():
                properties['#time'] = datetime.datetime.now()
            else:
                try:
                    time_temp = properties.get('#time')
                    if isinstance(time_temp, datetime.datetime) or isinstance(time_temp, datetime.date):
                        pass
                    else:
                        raise TGAIllegalDataException('#time only with datetime.datetime or datetime.date')
                except Exception as e:
                    raise TGAIllegalDataException(e)
            for key, value in properties.items():
                if not is_str(key):
                    raise TGAIllegalDataException("property key must be a str. [key=%s]" % str(key))
                if value is None:
                    continue
                if len(key) > 50:
                    raise TGAIllegalDataException("the max length of property key is 50. [key=%s]" % str(key))
                if not key_pattern.match(key):
                    raise TGAIllegalDataException(
                        "type[%s] property key must be a valid variable name. [key=%s]" % (action_type, str(key)))

                if not is_str(value) and not is_int(value) and not isinstance(value, (float)) and not isinstance(value,
                                                                                                                 datetime.datetime) and not isinstance(
                        value, datetime.date):
                    raise TGAIllegalDataException(
                        "property value must be a str/int/float/datetime/date. [value=%s]" % type(value))
                if 'user_add' == action_type.lower() and not self.__number(value) and not key.startswith('#'):
                    raise TGAIllegalDataException('user_add must be number')
                if isinstance(value, datetime.datetime):
                    properties[key] = value.strftime('%Y-%m-%d %H:%M:%S') + ".000"
                elif isinstance(value, datetime.date):
                    properties[key] = value.strftime('%Y-%m-%d')

    def __number(self, s):
        if is_int(s):
            return True
        if isinstance(s, float):
            return True
        return False

    def __getKeyNamePattern(self, type):
        if 'track' == type:
            return self.track_pattern
        else:
            return self.user_pattern

    def clear_super_properties(self):
        """
        删除所有已设置的事件公共属性
        """
        self.__super_properties = {
            '#lib': 'tga_python_sdk',
            '#lib_version': SDK_VERSION,
        }

    def set_super_properties(self, properties):
        """
        设置每个事件都带有的一些公共属性，当 track 的 properties 和 super properties 有相同的 key 时，将采用 track 的

        :param super_properties 公共属性
        """
        self.__super_properties.update(properties)


class LoggingConsumer(object):
    """
    将数据使用 logging 库输出到指定路径，并默认按天切割
    """

    # class AsyncFlushThread(threading.Thread):
    #     """
    #     发送数据的独立线程，在这里执行实际的网络请求。
    #     """
    #
    #     def __init__(self, consumer):
    #         super(LoggingConsumer.AsyncFlushThread, self).__init__()
    #         self._consumer = consumer
    #         # 用于实现安全退出
    #         self._stop_event = threading.Event()
    #         self._finished_event = threading.Event()
    #
    #     def stop(self):
    #         """
    #         需要退出时调用此方法，以保证线程安全结束。
    #         """
    #         self._stop_event.set()
    #         self._finished_event.wait()
    #
    #     def run(self):
    #         while True:
    #             # 如果 need_flush 标志位为 True，或者等待超过 flush_max_time，则继续执行
    #             self._consumer.need_flush.wait(self._consumer.flush_max_time)
    #             # 进行发送，如果成功则清除标志位
    #             if self._consumer.sync_flush():
    #                 self._consumer.need_flush.clear()
    #             # 发现 stop 标志位时安全退出
    #             if self._stop_event.isSet():
    #                 break
    #         self._finished_event.set()

    """
    @:param log_directory : 日志保存目录
    @:param queue_size : 队列大小
    @:param max_batch_size : 每次写入文件的最大数量
    @:param log_size : 单个日志文件的大小默认是1G
    """

    def __init__(self, log_directory, log_size=1024):
        self.log_directory = log_directory  # log文件保存的目录
        self._fileSize = log_size  # 单个log文件的大小

        # log
        self.logger = logging.getLogger('tga')
        self.sdf = '%Y-%m-%d'
        self.suffix = datetime.datetime.now().strftime(self.sdf)
        self.logger.propagate = False
        self.logger.setLevel(logging.INFO)
        self.handler = None
        if not self.log_directory.endswith("/"):
            self.log_directory = self.log_directory + "/"

        # 文件分隔后缀
        self._split_log_suffix = len([x for x in os.listdir(self.log_directory) if "log." + self.suffix in x])
        if self._split_log_suffix == 0:
            self._split_log_suffix = 0
        self.handler = self.__initLogger(self.log_directory, self.suffix, self._split_log_suffix)
        self.lock = threading.Lock()
        self.is_close = False

    def __initLogger(self, directory, date_suffix, file_suffix):
        filename = directory + "log." + date_suffix + "_" + str(file_suffix)
        if self.handler != None:
            self.logger.handlers[0].close()
            self.logger.removeHandler(self.handler)
        log_handler = logging.FileHandler(filename, mode='a')
        log_handler.setFormatter(logging.Formatter('%(message)s'))
        self.logger.addHandler(log_handler)
        return log_handler
    count = 0

    def send(self, msg):
        self.lock.acquire()
        try:
            if self.is_close:
                raise TGAException("tga had closed")
            if self.count % 100 == 0:
                self.sync_flush()
                self.count = 0
            self.logger.info(msg)
        except queue.Full as e:
            raise TGANetworkException(e)
        finally:
            self.count += 1;
            self.lock.release()

    def flush(self):
        pass

    def close(self):
        # 关闭时首先停止发送线程
        # self._flushing_thread.stop()
        # 循环发送，直到队列和发送缓存都为空
        # while not self._queue.empty() or not len(self._flush_buffer) == 0:
        #     self.sync_flush()
        self.is_close = True
        self.logger.handlers[0].close()

    def sync_flush(self, throw_exception=True):
        """
        执行一次同步发送。 throw_exception 表示在发送失败时是否向外抛出异常。
        """
        flush_success = False
        try:
            date_suffix = datetime.datetime.now().strftime(self.sdf)
            if self.suffix != date_suffix:
                self.suffix = date_suffix
                self._split_log_suffix = 0
                self.handler = self.__initLogger(self.log_directory, self.suffix, self._split_log_suffix)
            elif self.fileSizeOut(self.log_directory + "log." + self.suffix + "_" + str(self._split_log_suffix)):
                self.handler = self.__initLogger(self.log_directory, self.suffix, self._split_log_suffix)
                # if len(self._flush_buffer) == 0:
                #     for i in range(self._max_batch_size):
                #         if not self._queue.empty():
                #             self._flush_buffer.append(self._queue.get_nowait())
                #         else:
                #             break
                # if len(self._flush_buffer) > 0:
                #     try:
                #         for item in self._flush_buffer:
                #             self.logger.info(item)
                #         flush_success = True
                #         self._flush_buffer = []
                #     except TGAException as e:
                #         if throw_exception:
                #             raise e
        finally:
            pass
        return flush_success

    def fileSizeOut(self, filePath):
        fsize = os.path.getsize(filePath)
        fsize = fsize / float(1024 * 1024)
        if fsize >= self._fileSize:
            self._split_log_suffix += 1
            return True
        return False


class BatchConsumer(object):
    """
    默认的 Consumer实现，逐条、同步的发送数据给接收服务器。
    """

    def __init__(self, server_uri, appid, batch=10, timeout=1000, interval=3):
        """
        Consumer construct

        :param server_uri: 服务器的 URL 地址.
        :param appid: appid一个token，来自tga官网.
        :param timeout: 请求的超时时间，单位毫秒.
        :param interval: 推送数据的最大时间间隔.
        """
        self.__server_uri = server_uri
        self.__appid = appid
        self.__timeout = timeout
        self.__interval = interval

        self.__batch = min(batch, 200)
        self.__message_channel = []
        self.__last_flush = time.time()
        self.__httpconsumer = HttpConsumer(self.__server_uri, self.__appid, self.__timeout)

    def send(self, msg):
        if len(self.__message_channel) >= self.__batch or (
                    time.time() - self.__last_flush >= self.__interval and len(self.__message_channel) > 0):
            http_msg = self.__message_channel[:self.__batch]
            self.flush2(http_msg)
        self.__message_channel.append(msg)

    def flush2(self, msg):
        if len(self.__message_channel) > 0:
            self.__httpconsumer.send('[' + ','.join(msg) + ']')
            self.__last_flush = time.time()
            self.__message_channel = self.__message_channel[len(msg):]
    def flush(self):
        self.close()

    def close(self):
        if len(self.__message_channel) > 0:
            self.flush2(self.__message_channel)


class AsyncBatchConsumer(object):
    """
    异步、批量发送数据的 Consumer。使用独立的线程进行数据发送，当满足以下两个条件之一时进行数据发送:
    1. 数据条数大于预定义的最大值
    2. 数据发送间隔超过预定义的最大时间
    """

    def __init__(self, server_uir, appid, interval=10, flush_size=100, queue_size=100000):
        """
        初始化 AsyncBatchConsumer。

        :param server_uri: 服务器的 URL 地址。
        :param appid: 数据传输的token。
        :param interval: 两次发送的最大间隔时间，单位秒。
        :param flush_size: 队列缓存的阈值，超过此值将立即进行发送。
        :param queue_size: 缓存队列的大小。
        """
        self.__consumer = HttpConsumer(server_uir, appid, 500)
        self._flush_size = flush_size
        self.flush_max_time = interval

        self._queue = queue.Queue(queue_size)

        # 用于通知刷新线程应当立即进行刷新
        self.need_flush = threading.Event()
        self._flush_buffer = []

        # 初始化发送线程，并设置为 Daemon 模式
        self._flushing_thread = AsyncFlushThread(self)
        self._flushing_thread.daemon = True
        self._flushing_thread.start()

    def send(self, msg):
        # 这里不进行实际的发送，而是向队列里插入。如果队列已满，则抛出异常。
        if self._queue.qsize() >= self._flush_size:
            self.flush()
        try:
            self._queue.put_nowait(msg)
        except queue.Full as e:
            pass

    def flush(self):
        self.need_flush.set()

    def close(self):
        # 关闭时首先停止发送线程
        self._flushing_thread.stop()
        # 循环发送，直到队列和发送缓存都为空
        while not self._queue.empty() or not len(self._flush_buffer) == 0:
            self.sync_flush(True)

    def sync_flush(self, throw_exception=True):
        """
        执行一次同步发送。 throw_exception 表示在发送失败时是否向外抛出异常。
        """
        flush_success = False
        if len(self._flush_buffer) == 0:
            for i in range(self._flush_size):
                if not self._queue.empty():
                    self._flush_buffer.append(str(self._queue.get_nowait()))
                else:
                    break
        if len(self._flush_buffer) > 0:
            try:
                self.__consumer.send('[' + ','.join(self._flush_buffer) + ']')
                flush_success = True
                self._flush_buffer = []
            except TGAException as e:
                if throw_exception:
                    raise e
        return flush_success


# if __name__ == '__main__':
#     http = HttpConsumer('http://127.0.0.1:8991/logagent','quanjie')
#     data = '[{"#app_id": "quanjie","data": {"#account_id": "dojk0","#distinct_id": "F53A58ED-E5DA-4F18-B082-7E1228746E88","#type": "user_set","#time": "2017-12-18 14:37:28.527","properties": {"age": 24,},"#ip":"123.123.123.123"}},{"#app_id": "abc-ios","data": {"#account_id": "dojk0","#distinct_id": "F53A58ED-E5DA-4F18-B082-7E1228746E88","#type": "user_set","#time": "2017-12-18 14:37:28.527","properties": {"age": "0"}}}]'
#     print(http.send(data))

class HttpConsumer(object):
    def __init__(self, server_uri, appid, timeout=500):
        self.url = server_uri
        self.appid = appid
        self.timeout = timeout

    def send(self, data):
        """
        使用 Requests 发送数据给服务器，如果发生错误会抛出异常。
        """
        headers = {}
        headers['appid'] = self.appid
        headers['user-agent'] = 'tga-python-sdk'
        headers['version'] = SDK_VERSION

        for i in range(3):
            try:
                requests.post(self.url, data=self._gzip_string(data.encode("utf-8")), headers=headers,
                              timeout=self.timeout)
                return True
            except ConnectionError as e:
                time.sleep(0.5)

        raise TGAException("Data transmission failed")

    def _gzip_string(self, data):
        try:
            return base64.b64encode(gzip.compress(data))
        except AttributeError:
            import StringIO

            buf = StringIO.StringIO()
            fd = gzip.GzipFile(fileobj=buf, mode="w")
            fd.write(data)
            fd.close()
            return base64.b64encode(buf.getvalue())


class AsyncFlushThread(threading.Thread):
    """
    发送数据的独立线程，在这里执行实际的网络请求。
    """

    def __init__(self, consumer):
        threading.Thread.__init__(self)
        # super(AsyncBatchConsumer.AsyncFlushThread, self).__init__()
        self._consumer = consumer
        # 用于实现安全退出
        self._stop_event = threading.Event()
        self._finished_event = threading.Event()

    def stop(self):
        """
        需要退出时调用此方法，以保证线程安全结束。
        """
        self._stop_event.set()
        self._finished_event.wait()

    def run(self):
        while True:
            # 如果 need_flush 标志位为 True，或者等待超过 flush_max_time，则继续执行
            self._consumer.need_flush.wait(self._consumer.flush_max_time)
            # 进行发送，如果成功则清除标志位
            if self._consumer.sync_flush():
                self._consumer.need_flush.clear()
            # 发现 stop 标志位时安全退出
            if self._stop_event.isSet():
                break
        self._finished_event.set()
