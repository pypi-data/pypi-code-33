# coding=utf-8
import progressbar
import tarfile
from enum import Enum

from russell.client.module import ModuleClient

try:
    import _thread
except ImportError:
    import thread as _thread
import shutil
import websocket
from russell.client.base import RussellHttpClient
from russell.cli.utils import *
from russell.log import logger as russell_logger
from russell.exceptions import *

SOCKET_STATE = Enum('State', 'INIT UPLOADING FINISH FAILED')


class FsClient(RussellHttpClient):

    def __init__(self):
        self.ws_url = "wss://{host}:{port}".format(host=russell.russell_fs_host,
                                                   port=russell.russell_fs_port)
        self.FILE_NAME = ''
        self.STATE = SOCKET_STATE.INIT
        self.uploaded_size = 0
        self.data_config = None

        super(FsClient, self).__init__()

    def on_message(self, ws, message):
        russell_logger.debug(ws.header)
        russell_logger.debug(message)

        def start_sending():
            with open(self.FILE_NAME, 'rb') as f:
                # with progressbar.ProgressBar(maxval=int(ws.header.get('size', 0))) as bar:
                russell_logger.info("Start to send file with uploaded size {}".format(self.uploaded_size))
                bar = progressbar.ProgressBar(maxval=int(ws.header.get('size', 0))).start()
                try:
                    total_uploaded_size = self.uploaded_size
                    bar.update(total_uploaded_size)
                    f.seek(total_uploaded_size)
                    block_size = 1024 * 1024
                    msg = f.read(block_size)
                    while msg:
                        total_uploaded_size += len(msg)
                        ws.sock.send_binary(msg)
                        msg = f.read(block_size)
                        bar.update(total_uploaded_size)
                except:
                    pass
                finally:
                    pass

        russell_logger.debug('received {}'.format(message))
        resp_json = json.loads(message)
        code = resp_json.get('code')
        if code == 201:  # for resume uploaded size：
            self.uploaded_size = int(resp_json['data'])
        elif code == 200:  # to be modified
            if self.STATE == SOCKET_STATE.INIT:
                self.STATE = SOCKET_STATE.UPLOADING
                _thread.start_new_thread(start_sending, ())
            else:
                self.STATE = SOCKET_STATE.FINISH
                ws.close()
        elif code == 522:
            self.STATE = SOCKET_STATE.FAILED
            raise OverPermissionException()
        elif code == 532:
            self.STATE = SOCKET_STATE.FAILED
            raise RussellException()
        elif code == 533:
            self.STATE = SOCKET_STATE.FAILED
            raise OverSizeException()
        elif code == 534:
            self.STATE = SOCKET_STATE.FAILED
            raise ResumeInvalidException()
        elif code == 529:
            self.STATE = SOCKET_STATE.FAILED
            raise NotFoundException()
        elif code == 506:
            self.STATE = SOCKET_STATE.FAILED
            raise AuthenticationException()
        elif code == 507:
            self.STATE = SOCKET_STATE.FAILED
            raise AuthenticationException('Login expired!')
        else:
            self.STATE = SOCKET_STATE.FAILED
            raise ServiceBusyException()

    def clear_archive(self):
        shutil.rmtree(self.temp_dir)

    def on_error(self, ws, error):
        self.STATE = SOCKET_STATE.FAILED
        russell_logger.debug(str(error))
        ws.close()
        if isinstance(error, ClickException):
            # raised from on_message
            raise error

    def on_close(self, ws):
        russell_logger.debug('close connection to server')

    def on_open(self, ws):
        russell_logger.debug('setup connection to server')

    def socket_upload(self, file_type, filename, access_token, file_id, user_name, data_name, entity_id,
                      is_increment=False, temp_dir="./temp", is_compress=True, is_zip=False, is_direct=False,
                      resume=False):
        self.module_id = file_id
        self.entity_id = entity_id
        self.temp_dir = temp_dir
        self.data_config = DataConfigManager.get_config() if file_type == "data" else ExperimentConfigManager.get_config()
        self.is_increment = is_increment
        if is_direct:
            self.FILE_NAME = filename
        else:
            if is_zip:
                file_suffix = ".zip"
            elif is_compress:
                file_suffix = ".tar.gz"
            else:
                file_suffix = ".tar"
            self.FILE_NAME = os.path.join(temp_dir, file_id + file_suffix)
            if not resume:
                # compress the folder
                russell_logger.info('compressing files...')
                try:
                    if is_increment:  # 使用增量上传
                        self.compress_changed_files(is_compress, filename, file_type)
                    else:
                        self.FILE_NAME = shutil.make_archive(base_name=os.path.join(temp_dir, file_id + ".tar.gz"),
                                                             format='gztar' if is_compress else 'tar',
                                                             root_dir=filename,
                                                             owner=None,
                                                             group=None,
                                                             logger=russell_logger)
                except Exception as e:
                    raise e

        # compute md5 checksum
        hash_code = get_md5_checksum(self.FILE_NAME)
        compressed_size = os.path.getsize(self.FILE_NAME)
        russell_logger.info("compressed size: {} Bytes".format(compressed_size))

        # setup connection
        # websocket.enableTrace(True)
        header = {
            'access_token': access_token,
            'size': str(compressed_size),
            'hash_code': hash_code,
            'user_name': user_name,
            'data_name': data_name,
            'is_compress': str(is_compress),
            'is_zip': str(is_zip),
            "is_increment": str(self.is_increment and self.data_config.old_module_id is not None),
            "resume": str(resume)
        }
        if self.data_config.old_module_id:
            header["old_module_id"] = self.data_config.old_module_id
        if self.data_config.ignore_copy_list:
            header["ignore_list"] = self.data_config.ignore_copy_list
        web_socket = websocket.WebSocketApp(
            url=self.ws_url + "/{}/{}/".format(file_type, file_id),
            header=header,
            on_message=self.on_message,
            on_error=self.on_error,
            on_close=self.on_close
        )
        web_socket.on_open = self.on_open
        web_socket.run_forever()

    def socket_upload_tar(self, file_type, filename, access_token, file_id, user_name, data_name, entity_id,
                          is_increment=False, temp_dir="./temp", is_compress=True, resume=False):
        self.module_id = file_id
        self.entity_id = entity_id
        self.data_config = DataConfigManager.get_config() if file_type == "data" else ExperimentConfigManager.get_config()
        self.is_increment = is_increment
        # compress the folder
        russell_logger.info('compressing files...')
        self.temp_dir = temp_dir
        try:
            self.compress_changed_files(is_compress, filename, file_type, need_ignore=False)
            if is_compress:
                file_suffix = ".tar.gz"
            else:
                file_suffix = ".tar"
            self.FILE_NAME = os.path.join(temp_dir, file_id + file_suffix)
        except Exception as e:
            raise e
        # compute md5 checksum
        hash_code = get_md5_checksum(self.FILE_NAME)
        compressed_size = os.path.getsize(self.FILE_NAME)
        russell_logger.info("compressed size: {} Bytes".format(compressed_size))

        # setup connection
        # websocket.enableTrace(True)
        header = {
            'access_token': access_token,
            'size': str(compressed_size),
            'hash_code': hash_code,
            'user_name': user_name,
            'data_name': data_name,
            'is_compress': str(is_compress),
            "is_increment": str(self.is_increment and self.data_config.old_module_id is not None),
            "resume": str(resume)
        }
        if self.data_config.old_module_id:
            header["old_module_id"] = self.data_config.old_module_id
        if self.data_config.ignore_copy_list:
            header["ignore_list"] = self.data_config.ignore_copy_list

        web_socket = websocket.WebSocketApp(
            url=self.ws_url + "/{}/{}/".format(file_type, file_id),
            header=header,
            on_message=self.on_message,
            on_error=self.on_error,
            on_close=self.on_close
        )
        web_socket.on_open = self.on_open
        web_socket.run_forever()

    def compress_changed_files(self, is_compress, filename, module_type="data", need_ignore=False):
        with tarfile.open(os.path.join(self.temp_dir, self.module_id + ".tar.gz"),
                          "w:gz" if is_compress else "w") as tar:
            if need_ignore:
                ignore_list, whitelist = RussellIgnoreManager.get_list()
                ignore_list_expanded = ignore_list + ["{}/**".format(item) for item in ignore_list]
                ignore = ignore_patterns(*ignore_list_expanded)
                names = os.listdir(filename)
                if ignore is not None:
                    ignored_names = ignore(filename, names)
                else:
                    ignored_names = set()
            else:
                ignored_names = set()
            if self.is_increment:  # 请求API获取要最新版本文件md5
                filehash_req = ModuleClient().get_module_filehash(self.entity_id, module_type=module_type)
                if not filehash_req:
                    self.is_increment = False
                else:
                    filehash_dict = filehash_req['files']  # type: dict
                    dir_list = set(filehash_req['dirs'])
                    self.data_config.old_module_id = filehash_req['old_module_id']
                    ignore_copy_list = []
                    #  先和本地文件md5进行比对
                    for root, dirs, files in os.walk("."):
                        for d in dirs:
                            formatted_dirname = os.path.join(root, d).replace("." + os.sep, "").replace(os.sep, "/")
                            if formatted_dirname in dir_list:
                                dir_list.remove(formatted_dirname)
                        for file in files:
                            # 组装文件名
                            raw_filename = os.path.join(root, file)
                            formatted_filename = raw_filename.replace("." + os.sep, "").replace(os.sep, "/")
                            if formatted_filename in ignored_names:
                                continue
                            if formatted_filename in filehash_dict:  # 非新增文件
                                # upload_list.append(formatted_filename.replace("/", os.sep))
                                if get_md5_checksum(raw_filename) != filehash_dict.pop(formatted_filename):  # 修改过，上传不复制
                                    ignore_copy_list.append(formatted_filename)
                                    tar.add(raw_filename)
                            else:
                                tar.add(raw_filename)
                    # 遍历完毕，如果filehash_dict 仍存在属性，说明已删除
                    if filehash_dict:
                        ignore_copy_list.extend(filehash_dict.keys())
                    if dir_list:
                        ignore_copy_list.extend(dir_list)
                    self.data_config.ignore_copy_list = json.dumps(ignore_copy_list)
                    if module_type == "data":
                        DataConfigManager.set_config(self.data_config)
                    else:
                        ExperimentConfigManager.set_config(self.data_config)

            if not self.is_increment:
                exclude_files = [os.path.join(filename, n) for n in ignored_names]
                tar.add(filename, filter=lambda x: None if x.name in exclude_files else x)

    def get_state(self):
        return self.STATE
