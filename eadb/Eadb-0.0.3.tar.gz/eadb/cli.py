#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Time    : 2019-01-30 14:48
# Author  : gaojiewen
# Version : 1.0
# Desc    : 


import logging
import argparse
from eadb.adb import AndroidAdb
from eadb.__about__ import __description__, __version__

myadb = AndroidAdb()
parser = argparse.ArgumentParser(description=__description__)


def main_eadb():
    parser.add_argument(
        '-V', '--version', dest='version', action='store_true',
        help="show version")
    parser.add_argument(
        '-d', '--devices', dest='devices',
        help="show android devices id")
    parser.add_argument(
        '-n', '--name', dest='name',
        help="show android devices name")
    parser.add_argument(
        '-v', '--versions', dest='versions',
        help="show android devices version")
    parser.add_argument(
        '-s', '--screenshot', dest='screenshot',
        help="screen android devices and push to desktop")

    args = parser.parse_args()

    if args.version:
        print(__version__)
        exit(0)

    if args.versions:
        myadb.versions()
        exit(0)

    if args.devices:
        myadb.devices()
        exit(0)

    if args.name:
        myadb.deviceNames()
        exit(0)

    if args.screenshot:
        myadb.screenshot()
        exit(0)


def cmd_property(fun_name, help=None):
    """
    常用adb命令自定义装饰器
    :param fun_name: 常用adb封装命令的装饰器
    :param help: 帮助信息，可以为空
    :return: 返回结果
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            parser.add_argument('--id', dest='id', help=help)
            args = parser.parse_args()
            content = ''
            if args.id:
                content = getattr(myadb, fun_name)(id=args.id)
            else:
                content = getattr(myadb, fun_name)()
            return content
        return wrapper
    return decorator


@cmd_property('versions', help='get android devices version')
def get_version():
    pass


@cmd_property('screenshot', help="screen android devices and push to desktop")
def get_screenshot():
    pass


@cmd_property('deviceNames', help='show android devices name')
def get_device_name():
    pass

