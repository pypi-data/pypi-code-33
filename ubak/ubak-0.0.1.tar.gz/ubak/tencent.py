# -*- coding=utf-8
from qcloud_cos import CosConfig
from qcloud_cos import CosS3Client
import ConfigParser
import sys
import os
import logging
import time

logging.basicConfig(level=logging.INFO, stream=sys.stdout)


def init():
    config = {}

    # create config file
    if(not os.path.exists('ubak.conf')):
        if(raw_input('Detect no config file,do You want to create your config file now? (Y/n):') != 'n'):
            with open('ubak.conf', 'w') as cf:
                cf.writelines('[tCloud]\n')
                ops = ['secret_id', 'secret_key', 'region', 'scheme', 'bucket']
                for op in ops:
                    s = 'Please enter your ' + op + ':'
                    content = raw_input(s)
                    line = op + ' = ' + content + '\n'
                    cf.writelines(line)
                cf.writelines('\n')
                cf.writelines('[local]\n')
                ops = ['sql_pwd']
                for op in ops:
                    s = 'Please enter your ' + op + ':'
                    content = raw_input(s)
                    line = op + ' = ' + content + '\n'
                    cf.writelines(line)
        else:
            os._exit(0)

    # load config file
    conf = ConfigParser.ConfigParser()
    conf.read('ubak.conf')
    # tencent cloud config
    config['secret_id'] = conf.get('tCloud', 'secret_id')
    config['secret_key'] = conf.get('tCloud', 'secret_key')
    config['region'] = conf.get('tCloud', 'region')
    config['token'] = None  # 暂不支持临时上传
    config['scheme'] = conf.get('tCloud', 'scheme')

    # bucket config
    config['bucket'] = conf.get('tCloud', 'bucket')

    # mysql config
    config['sql_pwd'] = conf.get('local', 'sql_pwd')
    return config


def ubak():
    config = init()

    # show databases
    sql = 'mysql -uroot -p' + config['sql_pwd'] + ' ' + '-e "show databases;"'
    os.system(sql)

    # local config
    t = time.strftime("%Y%m%d", time.localtime())
    config['database'] = raw_input("chose a database you want to backup:")
    config['file_name'] = config['database'] + '-' + t + '.sql'
    config['file_path'] = config['database'] + '.sql'

    sql = 'mysqldump -uroot -p' + \
        config['sql_pwd'] + ' ' + config['database'] + \
        ' > ' + config['file_path']
    os.system(sql)

    Tconfig = CosConfig(Region=config['region'], SecretId=config['secret_id'],
                        SecretKey=config['secret_key'], Token=config['token'], Scheme=config['scheme'])

    client = CosS3Client(Tconfig)

    response = client.upload_file(
        Bucket=config['bucket'],
        LocalFilePath=config['file_path'],
        Key=config['file_name'],
        PartSize=10,
        MAXThread=10,
        EnableMD5=False
    )
    print('\033[1;42;40m Success! \033[0m ')
    print('File\'s ETag is:')
    print(response['ETag'])


if __name__ == "__main__":
    ubak()
