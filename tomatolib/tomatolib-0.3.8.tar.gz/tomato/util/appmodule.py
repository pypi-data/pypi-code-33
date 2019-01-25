#!/usr/bin/python
# -*- coding:utf-8 -*-

from abc import ABCMeta, abstractmethod


class AppModule(metaclass=ABCMeta):
    def __init__(self, *args, **kwargs):
        super(AppModule, self).__init__()

    def run(self):
        pass

    @abstractmethod
    def setup(self):
        pass

    @abstractmethod
    def destroy(self):
        pass
