import os
import json
import random
import string
import requests
from io import BytesIO
class DPResponse(object):
    ok = False
    text = None

    def __init__(self, ok, text):
        self.ok = ok
        self.text = text


class Uploader(object):
    r"""
    params:file_name 物理文件路径  
    params:data 合并文件接口附带的参数,数据集相关参数  
    params:args 上传接口upload_url & 合并接口merge_url 
    """
    def __init__(self, file_name, data, **args):
        r"""
        params:file_name 物理文件路径  
        params:data 合并文件接口附带的参数,数据集相关参数  
        params:args 上传接口upload_url & 合并接口merge_url 
        """
        if not os.path.exists(file_name):
            raise Exception('File not exist!')

        self._upload_url = args.get('upload_url')
        self._merge_url = args.get('merge_url')

        if not self._upload_url:
            raise Exception('upload_url is required')
        if not self._merge_url:
            raise Exception('merge_url is required')
        
        _jwt_token = args.get('jwt_token')

        self._headers = None
        if _jwt_token:
          self._headers = {'Authorization': _jwt_token}
        
        self._file_name = file_name
        self._data = data
        self._done = False

    def start(self):
        try:
            self._reset_task_id()
            self._push_part_file()

            if not self._done:
                self._part_merge()

            return DPResponse(True, self.text)
        except Exception as err:
            return DPResponse(False, str(err))
        finally:
            self._done = True

    def _reset_task_id(self):
        self.task_id = 'wu_{}'.format(
            ''.join(random.sample(string.ascii_letters + string.digits, 28)))

    # slice
    def _push_part_file(self):
        
        _file_size = os.path.getsize(self._file_name)

        # 小文件时提前给文件存储接口发送done状态，提醒直接合并
        self._done = _file_size <= 20 * 1024 * 1024
        _data = {'done': self._done}
        
        with open(self._file_name, 'rb') as f:
            _chunk = 1

            while True:
                part_bytes = f.read(20 * 1024 * 1024)
                if not part_bytes:
                    break
                files = {'file': (self.task_id, BytesIO(part_bytes), 'application')}
                _data['task_id'] = self.task_id
                _data['chunkNumber'] = _chunk

                _res = requests.post(self._upload_url, files=files, data=dict(_data, **self._data), headers=self._headers)
                if not _res.ok:
                    raise Exception('Encountered an error in pushing a slice, {}'.format(_res.text))
                _chunk += 1
            
            self.text = _res.text

    # merge
    def _part_merge(self):
        self._data['task_id'] = self.task_id
        _res = requests.put(self._merge_url, data=json.dumps(self._data), headers=self._headers)
        if not _res.ok:
            raise Exception('Encountered an error in merge all slices, {}'.format(_res.text))
        self.text = _res.text