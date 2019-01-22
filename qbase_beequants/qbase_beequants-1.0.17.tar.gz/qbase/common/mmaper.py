#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2018-8-6 15:40:03
# @Author  : datachain

import mmap
import logging

class Mmaper:
    __openMode = ''
    __fileName = ''
    __sizeOfMmap = ''
    __mmap = None
    log = None

    def __init__(self, fileName, sizeOfMmap, openMode):
        self.__fileName = fileName
        self.__openMode = openMode
        self.log = logging.getLogger()
        if openMode == "W":
            self.__sizeOfMmap = sizeOfMmap
            self._getWriteMmapWithFile()
        else:
            self._getReadMmapWithFile()

    def getMmap(self):
        if self.__mmap != None:
            return self.__mmap
        else:
            self.log.error("mmap is not init")
            return False

    def _getWriteMmapWithFile(self):
        try:
            f = open(self.__fileName, "w")
            f.write('\x00' * self.__sizeOfMmap)
            f.close()

            f = open(self.__fileName, 'r+')
            self.__mmap = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_WRITE)
        except Exception as e:
            self.log.error("getWriteMmapWithFile error is %s " %e)

    def _getReadMmapWithFile(self):
        try:
            f = open(self.__fileName, 'r')
            self.__mmap = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
        except Exception as e:
            self.log.error("getReadMmapWithFile error is %s " %e)


    def writeDataToMmap(self, data):
        try:
            if self.__mmap != None:
                self.__mmap.seek(0)
                self.__mmap.write(data)
                self.__mmap.flush()
            else:
                self.log.info("mmap is not init")
                return False
        except Exception as e:
            self.log.error("writeDataToMmap error is %s " %e)
            return False


    def readDataFromMmap(self):
        try:
            if self.__mmap != None:
                self.__mmap.seek(0)
                data = self.__mmap.read()
                return data
            else:
                self.log.info("mmap is not init")
                return False
        except Exception as e:
            self.log.error("readDataFromMmap error is %s " %e)
            return False

    def closeMmap(self):
        try:
            if self.__mmap != None:
                self.__mmap.close()
        except Exception as e:
            self.log.error("closeMmap error is %s " %e)
            return False
