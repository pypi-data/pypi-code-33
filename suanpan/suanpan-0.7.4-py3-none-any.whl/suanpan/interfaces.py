# coding=utf-8
from __future__ import print_function

import abc
import argparse

from suanpan import objects
from suanpan.dw import dw
from suanpan.log import logger
from suanpan.mq import mq
from suanpan.mstorage import mstorage
from suanpan.storage import storage


class HasBaseServices(abc.ABC):
    ENABLED_BASE_SERVICES = {"mq", "mstorage", "dw", "storage"}

    @classmethod
    def setBaseServices(cls, args):
        mapping = {
            "mq": cls.setMQ,
            "mstorage": cls.setMStorage,
            "dw": cls.setDataWarehouse,
            "storage": cls.setStorage,
        }
        setters = [mapping.get(s) for s in cls.ENABLED_BASE_SERVICES]
        if not all(setters):
            raise Exception(
                "Unknown base serivces: {}".format(
                    set(cls.ENABLED_BASE_SERVICES) - set(mapping.keys())
                )
            )
        for setter in setters:
            setter(args)

    @classmethod
    def setMQ(cls, args):
        return mq.setBackend(**cls.defaultArgumentsFormat(args, mq.ARGUMENTS))

    @classmethod
    def setMStorage(cls, args):
        return mstorage.setBackend(
            **cls.defaultArgumentsFormat(args, mstorage.ARGUMENTS)
        )

    @classmethod
    def setDataWarehouse(cls, args):
        return dw.setBackend(**cls.defaultArgumentsFormat(args, dw.ARGUMENTS))

    @classmethod
    def setStorage(cls, args):
        return storage.setBackend(**cls.defaultArgumentsFormat(args, storage.ARGUMENTS))

    @abc.abstractmethod
    def getArguments(self, *args, **kwargs):
        pass

    @abc.abstractmethod
    def transformArguments(self, *args, **kwargs):
        pass

    def parseArgs(self):
        return self.parseArguments(self.getArguments())

    @classmethod
    def parseArguments(cls, arguments, *args, **kwargs):
        parser = argparse.ArgumentParser(*args, **kwargs)
        for arg in arguments:
            arg.addParserArguments(parser)
        return parser.parse_known_args()[0]

    @classmethod
    def loadArguments(cls, args, arguments):
        return {arg.key: arg.load(args) for arg in arguments}

    @classmethod
    def formatArguments(cls, context, arguments):
        return {arg.key: arg.format(context) for arg in arguments}

    @classmethod
    def cleanArguments(cls, context, arguments):
        return {arg.key: arg.clean(context) for arg in arguments}

    @classmethod
    def defaultArgumentsFormat(cls, args, arguments):
        arguments = (arg.key.replace("-", "_") for arg in arguments)
        return {
            cls.defaultArgumentKeyFormat(arg): getattr(args, arg) for arg in arguments
        }

    @classmethod
    def defaultArgumentKeyFormat(cls, key):
        return cls.toCamelCase(cls.removePrefix(key))

    @classmethod
    def removePrefix(cls, string, delimiter="_", num=1):
        pieces = string.split(delimiter)
        pieces = pieces[num:] if len(pieces) > num else pieces
        return delimiter.join(pieces)

    @classmethod
    def toCamelCase(cls, string, delimiter="_"):
        camelCaseUpper = lambda i, s: s[0].upper() + s[1:] if i and s else s
        return "".join(
            [camelCaseUpper(i, s) for i, s in enumerate(string.split(delimiter))]
        )


class HasLogger(objects.HasName):
    def __init__(self):
        super(HasLogger, self).__init__()
        logger.setLogger(self.name)

    @property
    def logger(self):
        return logger
