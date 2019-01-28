#! /usr/bin/env python3
# -*- coding: utf-8 -*-

"""
@Version : python3.6
@Author  : LiuSQ
@Time    : 2019/1/28 14:47
@Describe: 
"""
import os


class FileHelper:
    """
        操作文件工具类
    """

    def __init__(self):
        pass

    @staticmethod
    def del_file(path):
        """
        删除文件夹下全部文件
        :param path:
        """
        ls = os.listdir(path)
        for i in ls:
            c_path = os.path.join(path, i)
            if os.path.isdir(c_path):
                del_file(c_path)
            else:
                os.remove(c_path)

    @staticmethod
    def read_file(file_path="", encoding="utf-8"):
        """
        读取一个文件
        :param file_path: 路径
        :param encoding: 编码
        :return: 文件中的内容
        """
        try:
            with open(file_path, encoding=encoding) as f:
                return f.read()
        except BaseException as e:
            print("Error: %s " % e)

    @staticmethod
    def mk_path(path):
        """
        创建一个路径
        :param path: 路径名
        :return: None
        """
        if not os.path.exists(path):
            os.makedirs(path)

    @staticmethod
    def mk_file(path):
        """
        创建一个文件
        :param path: 路径名
        :return: None
        """
        if not os.path.exists(path):
            os.mkdir(path)

    @staticmethod
    def write_file(content="", file_path="", encoding="utf-8"):
        """
        写入一个文件
        :param content: 写入文件的内容
        :param file_path: 文件的路径
        :param encoding: 编码
        :return: 是否成功
        """
        try:
            with open(file_path, "w", encoding=encoding) as f:
                f.write(content)
                return True
        except BaseException as e:
            print("Error: %s " % e)
            return False
