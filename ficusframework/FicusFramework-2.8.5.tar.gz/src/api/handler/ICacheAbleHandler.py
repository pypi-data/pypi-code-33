from abc import abstractmethod

from api.exceptions import IllegalArgumentException
from client import ScheduleCacheClient

CACHE_PREFIX = "sobeyficus."


class ICacheAbleHandler:
    """
    缓存操作的接口
    """

    @abstractmethod
    def get_code_thread_local(self):
        """
        需要实现的方法,返回一个 thread_local对象
        :return:
        """

    def set_cache_value(self, key, value):
        """
        放入缓存
        :param key:
        :param value:
        :return:
        """
        if key is None or value is None:
            raise IllegalArgumentException("设置任务缓存失败,传入的参数不合法")
        ScheduleCacheClient.set_value(self.__generate_key(key), value)

    def set_cache_value_if_absent(self, key, value):
        """
        放入缓存
        :param key:
        :param value:
        :return:
        """
        if key is None or value is None:
            raise IllegalArgumentException("设置任务缓存失败,传入的参数不合法")
        return ScheduleCacheClient.set_if_absent(self.__generate_key(key), value)

    def get_cache_value(self, key):
        """
        获取缓存
        :param key:
        :return:
        """
        if key is None:
            raise IllegalArgumentException("获取任务缓存失败,传入的参数不合法")
        return ScheduleCacheClient.get(self.__generate_key(key))

    def delete_cache_value(self, key):
        """
        删除缓存
        :param key:
        :return:
        """
        if key is None:
            raise IllegalArgumentException("删除任务缓存失败,传入的参数不合法")
        ScheduleCacheClient.delete(self.__generate_key(key))

    def __generate_key(self, key):
        """
        生成key
        :param key:
        :return:
        """
        return CACHE_PREFIX + self.get_code_thread_local().key + "." + key

    def set_local_code(self, code):
        """
        设置key
        :param code:
        :return:
        """
        self.get_code_thread_local().key = code

    def clear_local_code(self):
        """
        清空key
        :return:
        """
        self.get_code_thread_local().key = None
