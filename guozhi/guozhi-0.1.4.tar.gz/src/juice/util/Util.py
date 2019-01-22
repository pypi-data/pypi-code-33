#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os
import time


def create_client_id(user_name):
    return user_name + time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))


def _execute_command(shell_command):
    """
    在操作系统上执行命令
    :param shell_command: shell命令
    :return:
    """
    return os.popen(shell_command).readline().strip()


def get_raspberry_prop_info(command):
    """
    获取树莓派系统动态属性
    :param command: 标签命令
    :return:
    """
    command_dict = {
        # 核心电压
        "measure_volts_core": _execute_command("vcgencmd measure_volts core | awk -F '=' '{print $2}'"),
        # 温度
        "measure_temp": _execute_command("vcgencmd measure_temp | awk -F '=' '{print $2}'"),
        # cpu占内存
        "get_mem_arm": _execute_command("vcgencmd get_mem arm | grep arm | awk -F '=' '{print $2}'"),
        # gpu占内存
        "get_mem_gpu": _execute_command("vcgencmd get_mem gpu | grep gpu | awk -F '=' '{print $2}'")
    }
    return command_dict.get(command, 'no command')


def get_raspberry_sys_info():
    """
    获取树莓派系统关键信息
    :return:
    """
    return {
        # 版本代号
        "revision": _execute_command("cat /proc/cpuinfo | grep 'Revision' | awk '{print $3}'"),
        # 序列号
        "sn": _execute_command("cat /proc/cpuinfo | grep 'Serial' | awk '{print $3}'")
    }
