# -*- coding: utf-8 -*-

from os import listdir, makedirs, mkdir
from os.path import isfile, join, split, isdir, exists

import requests
from pandas.core.frame import DataFrame


class FileUtil:
    '''文件工具类'''

    @staticmethod
    def is_file(file):
        return isfile(file)

    @staticmethod
    def is_dir(file):
        return isdir(file)

    @staticmethod
    def list_children(dir, abs=False):
        '''
        列出文件和子目录
        :param dir: 目录
        :param abs: 返回是否带绝对路径
        :return:
        '''
        assert isdir(dir), "非法目录"
        if abs:
            return [join(dir, f) for f in listdir(dir)]
        else:
            return listdir(dir)

    @staticmethod
    def list_files(dir, abs=False):
        '''
        列出文件
        :param dir: 目录
        :param abs: 返回是否带绝对路径
        :return:
        '''
        assert isdir(dir), "非法目录"
        if abs:
            return [join(dir, f) for f in listdir(dir) if isfile(join(dir, f))]
        else:
            return [f for f in listdir(dir) if isfile(join(dir, f))]

    @staticmethod
    def list_dirs(dir, abs=False):
        '''
        列出子目录
        :param dir: 目录
        :param abs: 返回是否带绝对路径
        :return:
        '''
        assert isdir(dir), "非法目录"
        if abs:
            return [join(dir, f) for f in listdir(dir) if isdir(join(dir, f))]
        else:
            return [f for f in listdir(dir) if isdir(join(dir, f))]

    @staticmethod
    def rows_to_csv(records, path, desc=None):
        '''
        列表生成csv文件
        :param records: 列表
        :param path: 绝对路径
        :param desc: 表头
        '''
        df = DataFrame(records)
        if desc is not None:
            df.columns = desc
        df.to_csv(path, index=False)
        print "生成CSV文件:{}".format(path)

    @staticmethod
    def create_folder(folder, recursion=True):
        '''
        创建文件夹
        :param folder: 文件夹绝对路径
        :param recursion: 是否递归
        '''
        folder = folder.strip()
        if exists(folder):
            pass
        else:
            if recursion:
                makedirs(folder)
            else:
                mkdir(folder)
            print "目录 {} 创建成功".format(folder)

    @staticmethod
    def down_pic(url, file, force=True):
        '''不能用于多进程
        下载图片
        :param url: 图片地址
        :param file: 目标文件路径
        :param force: 是否覆盖生成
        :return:
        '''
        try:
            if isfile(file) and not force:
                return
            else:
                res = requests.get(url)
                if res.status_code == 200:
                    # 创建文件前序路径
                    FileUtil.create_folder(split(file)[0])
                    # 生成文件
                    with open(file, "wb+") as op:
                        op.write(res.content)
                else:
                    raise requests.HTTPError
        except Exception, e:
            print e
