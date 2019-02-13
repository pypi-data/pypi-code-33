#!/usr/bin/env python
#encoding: utf-8
#Date: 2018-10-20
#

from qiniu import Auth, put_file, etag
import qiniu.config

import sys
import os
import datetime


if sys.version_info.major == 2:
    import ConfigParser as configparser
elif sys.version_info.major == 3:
    import configparser


class qiniuInstance:
    '''
    上传中把一般文件和图片、css、js等静态文件区分开
    '''

    ## 定义私有变量
    __date_folder = datetime.datetime.now().strftime('%Y%m%d')
    __img_path = 'static/images/'
    __js_path = 'static/js/'
    __css_path = 'static/css/'
    __file_path = 'files/'

    # _qn_auth = Auth(__access_key, __secret_key)
    
    def __init__(self, configfile="", section="public", local_filename=None, file_type="file"):
        self.configfile = configfile
        self.section = section
        self.local_filename = local_filename
        self.file_type = file_type


    def getConfig(self):
        configdict = {}
        config = configparser.ConfigParser()
        config.read(self.configfile)
        configdict['access_key'] = config[self.section]['access_key']
        configdict['secret_key'] = config[self.section]['secret_key']
        configdict['bucket_name'] = config[self.section]['bucket_name']
        return configdict

    def upload_file(self):
        """
        上传函数
        """

        ## get config content
        config = self.getConfig()
        bucket = config['bucket_name']
        access_key = config['access_key']
        secret_key = config['secret_key']
        qn_auth = Auth(access_key, secret_key)

        real_filename = os.path.split(self.local_filename)[-1]
        if self.file_type == 'file':
            remote_filename = self.__file_path + self.__date_folder + '/' + real_filename
        elif self.file_type == 'img' or self.file_type == 'image':
            remote_filename = self.__img_path + self.__date_folder + '/' + real_filename
        elif self.file_type == 'js':
            remote_filename = self.__js_path + self.__date_folder + '/' + real_filename
        elif self.file_type == 'css':
            remote_filename = self.__css_path + self.__date_folder + '/' + real_filename
     
        ## get token
        token = qn_auth.upload_token(bucket, remote_filename, 3600)
        result, info = put_file(token, remote_filename, self.local_filename)

        if info.status_code == 200:
            print('upload [%s] successfully!' % result['key'])
