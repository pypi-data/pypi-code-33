#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Used internally by other framework components to provide logging in a simple and consistent manner.
"""
import logging


__all__ = ["LoggerMixin"]


class LoggerMixin:
    """
    Injects a logger into class scope with an appropriate name.
    
    Objects will use a logger adapter facade to enable MDC-like behaviour per object.
    """

    logger: logging.Logger

    def __init_subclass__(cls, **kwargs):
        cls.logger: logging.Logger = logging.getLogger(cls.__name__)

    def __init__(self, *args, **kwargs):
        logger = logging.getLogger(type(self).__name__)
        extra = {"object_id": id(self)}
        self.logger: logging.LoggerAdapter = logging.LoggerAdapter(logger, extra=extra)
