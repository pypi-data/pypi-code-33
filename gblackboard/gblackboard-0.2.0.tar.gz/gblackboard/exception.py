# -*- coding: utf-8 -*-


class BlackboardException(Exception):
    pass


class UnsupportedMemoryType(BlackboardException):
    pass


class DataException(BlackboardException):
    pass


class MemoryException(BlackboardException):
    pass


class NotCallable(BlackboardException):
    pass


# about data

class KeyNotString(DataException):
    pass


class UnsupportedDataType(DataException):
    pass


class ExistingKey(DataException):
    pass


class NotEditable(DataException):
    pass


class NonExistingKey(DataException):
    pass


# about Redis

class RedisException(MemoryException):
    pass


class RedisWrongConfig(RedisException):
    pass


class RedisNotConnected(RedisException):
    pass


# about save & load file

class FileIOException(BlackboardException):
    pass


class ReadWrongFile(FileIOException):
    pass


class NonExistingDirectory(FileIOException):
    pass


class UnsafeLoading(FileIOException):
    pass
