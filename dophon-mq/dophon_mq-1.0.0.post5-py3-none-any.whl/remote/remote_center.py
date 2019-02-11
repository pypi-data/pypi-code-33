import json
from datetime import time
from socketserver import ThreadingTCPServer, StreamRequestHandler
from dophon_mq.utils import *
from logging import Logger

trace_manager = {}

msg_queue = {}

logger = Logger(__name__)


def init_msg_queue(topic: str):
    """
    加载持久化消息
    :return:
    """
    for root, dirs, files in os.walk(remote_msg_pool + topic):
        if dirs:
            # 初始化标签
            for d in dirs:
                msg_queue[d] = []
                for r, ds, fs in os.walk(root + d):
                    if fs:
                        for f in fs:
                            with open(root + d + os.path.sep + f, 'r') as msg_file:
                                data = json.loads(msg_file.readline(), encoding='utf-8')
                                msg_queue[d].append(data)


class UnexpectedSocketError(Exception):
    pass


class MsgCenter(ThreadingTCPServer):
    _p_name_l = []
    _p_tunnel_cursor = {}

    def __init__(self, debug: bool = False, port: int = 58800, topic: str = ''):
        self._port = port
        init_msg_queue(topic)
        if debug:
            self.listen_p_book()
        super(MsgCenter, self).__init__(('0.0.0.0', port), SocketMsgHandler)
        self.start_server()

    # @threadable()
    def start_server(self):
        logger.info('监听端口 %s' % (str(self._port)))
        print('监听端口 %s' % (str(self._port)))
        self.serve_forever()

    @threadable()
    def listen_p_book(self):
        self.print_trace_manager()

    def print_trace_manager(self):
        while True:
            time.sleep(3)
            print(trace_manager)


class SocketMsgHandler(StreamRequestHandler):
    """
    远程消息隧道处理类
    """

    def handle(self):
        conn = self.request
        self.wfile.write(bytes('连接远程消息处理', encoding='utf-8'))
        ret_bytes = '1'
        while ret_bytes:
            ret_bytes = conn.recv(1024).strip()
            ret_str = str(ret_bytes, encoding="utf-8")
            # print(ret_str)
            if ret_bytes and ret_str:
                try:
                    data = eval(ret_str)
                    if isinstance(data, dict):
                        # 字典信息(生产信息)
                        self.recive_remote_msg(data, conn)
                    elif isinstance(data, list):
                        # 列表形式(消费信息)
                        self.push_remote_msg(data, conn)
                    else:
                        conn.send(bytes(json.dumps({
                            'error': '不能识别的消息类型'
                        }), encoding='utf-8'))
                except Exception as e:
                    conn.sendall(bytes(json.dumps({
                        'error': '远程消息中心发生错误',
                        'err_msg': str(e)
                    }), encoding='utf-8'))
                    raise e
            else:
                self.finish()

    def push_remote_msg(self, data, client_socket):
        for p_name in data:
            # 遍历消息信息
            # 从缓存获取消息
            if p_name in msg_queue and msg_queue[p_name]:
                msg_obj = msg_queue[p_name].pop(0)
                try:
                    client_socket.sendall(bytes(json.dumps(msg_obj), encoding='utf-8'))
                    ack_str = str(client_socket.recv(1024), encoding='utf-8')
                    ack_info = decode_ack_info(ack_str)
                    if ack_info['ack_code'] != '200':
                        # 消息消费失败
                        raise Exception('消息消费失败: %s' % ack_info['ack_msg'])
                    else:
                        # 消息消费成功
                        file_name = ack_info['ack_mark']
                        file = remote_msg_pool + p_name + os.path.sep + file_name
                        os.unlink(file)
                except PermissionError as pe:
                    logger.info(pe)
                    # 权限问题或操作冲突
                    msg_queue[p_name].append(msg_obj)
                except Exception as e:
                    raise e
            else:
                client_socket.sendall(bytes('none', encoding='utf-8'))

    def recive_remote_msg(self, data, client_socket):
        # 处理消息
        p_name = data['tag']
        msg_mark = data['msg_mark']
        # 写入自身消息缓存
        if p_name in msg_queue:
            msg_queue[p_name].append({
                msg_mark: data
            })
        else:
            msg_queue[p_name] = [{
                msg_mark: data
            }]
        # 写入本地文件
        if not os.path.exists(remote_msg_pool + p_name):
            os.mkdir(remote_msg_pool + p_name)
        with open(remote_msg_pool + p_name + os.path.sep + msg_mark, 'w') as file:
            json.dump({msg_mark: data}, file, ensure_ascii=False)
            client_socket.send(bytes(json.dumps({
                'msg_mark': msg_mark
            }), encoding='utf-8'))
