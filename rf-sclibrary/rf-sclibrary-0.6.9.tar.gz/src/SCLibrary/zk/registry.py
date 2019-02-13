# coding=utf-8
import time
import os
import socket
import struct
import random
from threading import Thread
import re
import sys
import urllib

from kazoo.protocol.states import KazooState
from kazoo.client import KazooClient


class Registry(object):
    """
    所有注册过的服务端将在这里
    interface=com.ofpay.demo.DemoService
    location = ip:port/url 比如 172.19.20.111:38080/com.ofpay.demo.DemoService2
    providername = servicename|version|group
    dict 格式为{interface:{providername:{ip+port:service_url}}}

    """
    _service_provides = {}

    def _do_event(self, event):
        """
        protect方法，处理回调，留给子类实现
        :param event:
        :return:
        """
        pass

    def subscribe(self, interface, **kwargs):
        """
        监听注册中心的服务上下线
        :param provide_name: 类似com.ofpay.demo.api.UserProvider这样的服务名
        :param kwargs: version , group
        :return: 无返回
        """
        pass

    def get_provides(self, interface, **kwargs):
        """
        获取已经注册的服务URL对象
        :param interface: com.ofpay.demo.api.UserProvider
        :param default:
        :return: 返回一个dict的服务集合
        """
        group = kwargs.get('group', '')
        version = kwargs.get('version', '')
        key = self._to_key(interface, version, group)
        second = self._service_provides.get(interface, {})
        return second.get(key, {})

    def event_listener(self, event):
        """
        node provides上下线的监听回调函数
        :param event:
        :return:
        """
        self._do_event(event)

    def _to_key(self, interface, versioin, group):
        """
        计算存放在内存中的服务的key，以接口、版本、分组计算
        :param interface: 接口 类似com.ofpay.demo.DemoProvider
        :param versioin: 版本 1.0
        :param group:  分组 product
        :return: key 字符串
        """
        return '{0}|{1}|{2}'.format(interface, versioin, group)


class ZookeeperRegistry(Registry):
    _connect_state = 'UNCONNECT'

    def __init__(self, zk_hosts):
        self.__zk = KazooClient(hosts=zk_hosts)
        self.__zk.add_listener(self.__state_listener)
        self.__zk.start()
        self.__zk.add_auth("digest","read:souche-read")

    def __state_listener(self, state):
        if state == KazooState.LOST:
            # Register somewhere that the session was lost
            self._connect_state = state
        elif state == KazooState.SUSPENDED:
            # Handle being disconnected from Zookeeper
            # print 'disconnect from zookeeper'
            self._connect_state = state
        else:
            # Handle being connected/reconnected to Zookeeper
            # print 'connected'
            self._connect_state = state

    def _do_event(self, event):
        # event.path 是类似/dubbo/com.ofpay.demo.api.UserProvider/providers 这样的
        # 如果要删除，必须先把/dubbo/和最后的/providers去掉
        # 将zookeeper中查询到的服务节点列表加入到一个dict中
        # zookeeper中保持的节点url类似如下
        provide_name = event.path[7:event.path.rfind('/')]
        if event.state == 'CONNECTED':
            children = self.__zk.get_children(event.path, watch=self.event_listener)
            self._compare_swap_nodes(provide_name, self.__unquote(children))
        if event.state == 'DELETED':
            children = self.__zk.get_children(event.path, watch=self.event_listener)
            self._compare_swap_nodes(provide_name, self.__unquote(children))


    def subscribe(self, interface, **kwargs):
        """
        监听注册中心的服务上下线
        :param interface: 类似com.ofpay.demo.api.UserProvider这样的服务名
        :return: 无返回
        """
        version = kwargs.get('version', '')
        group = kwargs.get('group', '')
        children = self.__zk.get_children('{0}/{1}/{2}'.format('dubbo', interface, 'providers'),watch=self.event_listener)
        provide = random.choice(children)
        provide = urllib.parse.unquote(provide)
        ip = re.findall(r"\d{0,3}\.\d{0,3}\.\d{0,3}\.\d{0,3}:\d{2,5}", provide)
        return  ip