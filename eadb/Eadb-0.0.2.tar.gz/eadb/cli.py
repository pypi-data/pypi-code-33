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


def get_version():
    parser.add_argument(
        '--id', dest='id',
        help="get android devices version")
    args = parser.parse_args()
    version = ''
    if args.id:
        version = myadb.versions(id=args.id)
    else:
        version = myadb.versions()
    print(version)


def screenshot():
    parser.add_argument(
        '--id', dest='id',
        help="screen android devices and push to desktop")
    args = parser.parse_args()
    if args.id:
        myadb.screenshot(id=args.id)
    else:
        myadb.screenshot()


def get_device_name():
    parser.add_argument(
        '--id', dest='id',
        help="show android device name")
    args = parser.parse_args()
    name = ''
    if args.id:
        name = myadb.deviceNames(id=args.id)
    else:
        name = myadb.deviceNames()
    print(name)
