import os
import json
import random
import string
import requests
from io import BytesIO
from aios_part_uploader.exceptions import FileTransError

class CSResponse(object):
    ok = False
    text = None

    def __init__(self, ok, text):
        self.ok = ok
        self.text = text

class Uploader(object):
    r"""文件存储服务NFS上传接口  
    params:sub_dir 文件在文件系统存放的目录  
    例如: 挂载点是/mnt/, sub_dir是/dev/dmp/1/..., file_name是c:\\test.txt
        最终会存放到的地址: 
            /mnt/dev/dmp/1/.../test.txt
        格式为<挂载点>/<中间路径>/<文件名>
        中间路径格式：
            <env>/<自定义>
        env是环境标记:
            prod:生产环境
            test:测试环境
            dev:开发环境
    params:file_name 物理文件路径  
    params:args 上传接口 upload_url & 合并接口 merge_url 
    
    文件分片上传阶段异常  
    FileTransError : File transfer failed (1)! xxx  

    分片合并阶段异常  
    FileTransError : File transfer failed (2)! yyy  
    """

    def __init__(self, sub_dir, file_name, **args):
        if not sub_dir:
            raise Exception('sub_dir is missing or invalidate!')
        if not os.path.exists(file_name):
            raise Exception('File not exist!')

        self._upload_url = args.get('upload_url')
        self._merge_url = args.get('merge_url')

        if not self._upload_url:
            raise Exception('upload_url is required!')
        if not os.path.basename(file_name):
            raise Exception('upload_url is invalid format!')
        if not self._merge_url:
            raise Exception('merge_url is required!')

        _jwt_token = args.get('jwt_token')
        
        self._headers = None
        if _jwt_token:
          self._headers = {'Authorization': _jwt_token}
        
        self._file_name = file_name
        self._sub_dir = sub_dir
        self._done = False

    def start(self):
        try:
            self._reset_task_id()
            self._push_part_file()

            if not self._done:
                self._part_merge()

            return CSResponse(True, self.text)
        except Exception as err:
            return CSResponse(False, str(err))
        finally:
            self._done = True

    def _reset_task_id(self):
        self.task_id = 'wu_{}'.format(
            ''.join(random.sample(string.ascii_letters + string.digits, 28)))

    # slice
    def _push_part_file(self):

        _chunk = 1
        _file_name = os.path.basename(self._file_name)
        _upload_data = {'task_id': self.task_id, 'sub_dir': self._sub_dir, 'filename': _file_name}

        _file_size = os.path.getsize(self._file_name)
        
        # 小文件时提前给文件存储接口发送done状态，提醒直接合并
        self._done = _file_size <= 20 * 1024 * 1024
        _upload_data['done'] = self._done
        
        with open(self._file_name, 'rb') as f:
            while True:
                # 每次读取20M
                part_bytes = f.read(20 * 1024 * 1024)
                if not part_bytes:
                    break

                _upload_data['chunkNumber'] = _chunk

                _file_name = os.path.basename(self._file_name)

                _files = {'file': (_file_name, BytesIO(part_bytes), 'application')}
                
                _res = requests.post(self._upload_url, files=_files, data=_upload_data, headers=self._headers)
                
                if not _res.ok and _res.status_code == 200:
                    raise FileTransError('File transfer failed (1)! {}'.format(_res.text))
                _chunk += 1

                self.text = _res.text

    # merge
    def _part_merge(self):
        _file_name = os.path.basename(self._file_name)
        _merge_data = {'sub_dir': self._sub_dir, 'task_id': self.task_id, 'filename': _file_name}
        _res = requests.put(self._merge_url, data=_merge_data, headers=self._headers)
        if not _res.ok:
            raise FileTransError('File transfer failed (2)! {}'.format(_res.text))
        self.text = _res.text
