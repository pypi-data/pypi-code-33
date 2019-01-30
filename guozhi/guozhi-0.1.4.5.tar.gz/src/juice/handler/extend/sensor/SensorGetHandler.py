#!/usr/bin/env python
# -*- coding:utf-8 -*-

import Adafruit_DHT
import RPi.GPIO as GPIO

from juice.handler.PropHandler import PropGetHandler
from juice.model.PropMessage import PropMessage

GPIO_STATUS = {-1: 'no mode,please input bcm or board', 0: 'LOW', 1: 'HIGH'}


class TempGetHandler(PropGetHandler):
    """
    温度传感器获取，实例化需要设置bcm编号
    """

    def __init__(self, gpio_bcm_num):
        self.gpio = gpio_bcm_num

    """
        传感器温度获取方法
        handle为必须实现的方法
        reply上行消息，返回给服务器
    """

    def handle(self, flag):
        self.reply(PropMessage(flag, self.temp()))

    def temp(self):
        sensor = Adafruit_DHT.DHT11
        humidity, temperature = Adafruit_DHT.read_retry(sensor, self.gpio)
        return 'Temp={0:0.1f}*C  Humidity={1:0.1f}%'.format(temperature, humidity)


class SoudGetHandler(PropGetHandler):
    """
    蜂鸣器状态获取，实例化需要设置bcm编号
    """

    def __init__(self, mode, gpio_num):
        self.mode = mode.lower()
        self.gpio = gpio_num

    """
        传蜂鸣器状态获取方法
        handle为必须实现的方法
        reply上行消息，返回给服务器
    """

    def handle(self, flag):
        self.reply(PropMessage(flag, GPIO_STATUS.get(GetGPIOStatus(self.mode, self.gpio))))


def GetGPIOStatus(mode, gpio_num):
    gpio_mode = {
        'bcm': GPIO.BCM,
        'board': GPIO.BOARD
    }
    mode_type = gpio_mode.get(mode.lower(), '')
    gpio = gpio_num
    if mode_type == '':
        return -1
    else:
        GPIO.setwarnings(False)
        GPIO.setmode(mode_type)
        GPIO.setup(gpio, GPIO.OUT)
        num = GPIO.input(gpio)
        GPIO.cleanup()
        return num
