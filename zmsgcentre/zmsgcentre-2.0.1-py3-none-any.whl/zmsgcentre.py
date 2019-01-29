# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：    zmsgcentre.py
   Author :       Zhang Fan
   date：         2018/10/2
   Description :
-------------------------------------------------
"""
__author__ = 'Zhang Fan'

import copy
import threading

_message_saver = {}

_main_lock = threading.Lock()
_msg_tag_lock_saver = {}


def create_receiver(msg_tag: str, receiver_func, priority=999):
    '''
    创建一个接收器
    :param msg_tag: 设置接收哪个消息标签的信息
    :param receiver_func: 接收器触发函数
    :param priority: 优先级(数字越小越先收到广播, 距离相同的接收器顺序随机)
    '''
    assert hasattr(receiver_func, '__call__')

    with _main_lock:
        if msg_tag not in _message_saver:
            _message_saver[msg_tag] = {}
            _msg_tag_lock_saver[msg_tag] = threading.Lock()

        receiver_saver = _message_saver[msg_tag]
        msg_tag_lock = _msg_tag_lock_saver[msg_tag]

    with msg_tag_lock:
        receiver_saver[receiver_func] = priority


def destroy_receiver(msg_tag: str, receiver_func):
    '''
    销毁一个接收器
    :param msg_tag: 消息标签
    :param receiver_func: 接收器触发函数
    '''
    with _main_lock:
        if msg_tag not in _message_saver:
            return

        receiver_saver = _message_saver[msg_tag]
        msg_tag_lock = _msg_tag_lock_saver[msg_tag]

    with msg_tag_lock:
        if receiver_func in receiver_saver:
            del receiver_saver[receiver_func]


def destroy_receiver_of_msg_tag(msg_tag: str):
    '''
    销毁指定消息标签的所有接收器
    :param msg_tag: 消息标签
    '''
    with _main_lock:
        if msg_tag not in _message_saver:
            return

        del _message_saver[msg_tag]
        del _msg_tag_lock_saver[msg_tag]


def destroy_all_receiver():
    '''
    销毁所有的接收器
    '''
    with _main_lock:
        _message_saver.clear()
        _msg_tag_lock_saver.clear()


def _receiver_saver_priority_sorted(item):
    return item[1]


def send(msg_tag: str, *args, stop_send_flag=None, **kwargs):
    '''
    发送数据
    :param msg_tag: 消息标签
    :param stop_send_flag: 停止发送标记, 如果有一个接收器返回这个标记则停止发送(内部使用is判断)并且返回True
    :return: 返回一个列表, 这个列表包含所有接收器的返回值(无序), 无接收器返回一个空列表
    '''
    with _main_lock:
        if msg_tag not in _message_saver:
            return []

        receiver_saver = _message_saver[msg_tag]
        msg_tag_lock = _msg_tag_lock_saver[msg_tag]

    with msg_tag_lock:
        receiver_saver = copy.copy(receiver_saver)

    receiver_saver = sorted(receiver_saver.items(), key=_receiver_saver_priority_sorted)

    result_list = []
    for receiver_func, priority in receiver_saver:
        result = receiver_func(*args, **kwargs)
        if result is stop_send_flag and stop_send_flag is not None:
            return True
        result_list.append(result)

    return result_list


def sender(msg_tag: str, stop_send_flag=None):
    '''
    装饰器(发送者)
    :param msg_tag: 消息标签
    :param stop_send_flag: 停止发送标记, 如果有一个接收器返回这个标记则停止发送(内部使用is判断)并且返回True
    '''

    def decorator(sender_func):
        def new_func(*args, **kwargs):
            return send(msg_tag, *args, stop_send_flag=stop_send_flag, **kwargs)

        return new_func

    return decorator


def receiver(msg_tag: str, priority=999):
    '''
    装饰器(接收器)
    :param msg_tag: 消息标签
    :param priority: 优先级(数字越小越先收到广播, 数字相同的接收器顺序随机)
    '''

    def decorator(receiver_func):
        create_receiver(msg_tag, receiver_func, priority=priority)
        return receiver_func

    return decorator
