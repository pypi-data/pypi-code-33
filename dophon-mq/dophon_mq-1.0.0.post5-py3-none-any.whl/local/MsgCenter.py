"""
消息处理中心

处理消息发送信息落地
初始化消息通道（单一消息通道模式，集群消息通道模式）
暂时参照jms协议(点对点消息ps)
消息消费使用拉(pull)模式(后期增加推模式)
"""
import json
import re
import time
from socket import *
from threading import Timer

from logging import Logger
from dophon_mq import bone_data
from dophon_mq.utils import *
from dophon_mq.utils import threadable

logger = Logger(__name__)


@singleton
def get_center(debug: bool = False, remote_center: bool = False):
    ins_obj = MsgCenter(debug, remote_center)
    if remote_center:
        logger.info('开启远程消息')
    return ins_obj


def get_socket():
    """
    获取套接字对象
    :return:
    """
    __socket = socket(AF_INET, SOCK_STREAM)
    __socket.connect((properties.mq.get('remote_address'), properties.mq.get('remote_port')))
    return __socket


class MsgCenter:
    _p_name_l = []
    _p_tunnel_cursor = {}

    def __init__(self, debug: bool, remote: bool = False):
        logger.info('初始化消息中心')
        if debug:
            self.listen_p_book()
        # 记录远程中心标识
        self._remote_flag = remote
        if remote:
            self.server_forever()

    @threadable()
    def server_forever(self):
        """
        挂起本地服务
        :return:
        """
        while True:
            # 挂起100秒
            time.sleep(100)

    def write_p_book(self, p_name):
        """
        登记生产属性名单
        :param p_name: 生产名
        :param p_id: 生产标识（用作生产校验）
        :return:
        """
        if p_name not in self._p_name_l \
                and p_name not in self._p_tunnel_cursor \
                and not self._p_tunnel_cursor.get(p_name):
            self._p_name_l.append(p_name)
            if self._remote_flag:
                m_tunnel = SocketMsgTunnel(p_name)
                self._p_tunnel_cursor[p_name] = m_tunnel
            else:
                m_tunnel = MsgTunnel(p_name)
                self._p_tunnel_cursor[p_name] = m_tunnel

    @threadable()
    def listen_p_book(self):
        self.print_trace_manager()

    def print_trace_manager(self):
        while True:
            time.sleep(3)
            print(trace_manager)

    @threadable()
    def do_send(self, msg, p_name, delay):
        """
        发送消息
        :param msg: 消息体
        :param p_name: 消息标签
        :param delay: 延时
        :return:
        """
        return self.do_remote_send(msg, p_name, delay) if self._remote_flag else self.do_local_send(msg, p_name, delay)

    def do_local_send(self, msg, p_name, delay):
        # 使用定时器发送消息
        # timer = Timer(delay, self._p_tunnel_cursor[p_name].recv_msg, [msg])
        # timer.start()
        # 利用自身绑定通道发送消息
        self._p_tunnel_cursor[p_name].recv_msg(msg)
        self._p_tunnel_cursor[p_name].insert_msg(p_name)

    def do_remote_send(self, msg, p_name, delay):
        """
        发送消息到消息通道
        :param msg:
        :param p_name: 消息标签
        :param delay: 延时
        :return: 消息体
        """
        # 使用定时器发送消息
        # timer = Timer(delay, self.remote_send_stack, [msg, p_name])
        # timer.start()
        # 阻塞式发送
        self.remote_send_stack(msg, p_name)

    def remote_send_stack(self, msg, p_name):
        """
        远程消息发送栈
        :param msg:
        :param p_name:
        :return:
        """
        self._p_tunnel_cursor[p_name].send_msg(msg)
        self._p_tunnel_cursor[p_name].insert_msg(p_name)

    # 启用多线程监听消息
    @join_threadable
    def do_get(self, p_name, delay: int, f, kwargs, arg_name: str):
        """
        从消息管道获取消息
        采用回调形式执行消息
        :param p_name:
        :param delay:
        :return:
        """
        if callable(f):
            # 参数过滤
            while True:
                get_method = self.do_remote_get if self._remote_flag else self.do_local_get
                msg_data = get_method(p_name, delay)
                if not msg_data or msg_data == 'none':
                    time.sleep(1)
                else:
                    kwargs[arg_name] = msg_data
                    # 执行回调方法
                    try:
                        f(**kwargs)
                    except Exception as e:
                        # 执行失败重新发送消息
                        self.do_send(msg_data, p_name, delay)
        else:
            print(f, '不是个方法')

    def do_local_get(self, p_name: str, delay: int):
        """
        从本地消息管道获取消息
        :param p_name:
        :param delay:
        :return:
        """
        if p_name and p_name in self._p_tunnel_cursor:
            msg_data = self._p_tunnel_cursor[p_name].query_msg(delay)
            return msg_data
        else:
            logger.info('&s%s' % (p_name, '不存在'))

    def do_remote_get(self, p_name: str, delay: int):
        """
        从远程消息中心获取消息
        :param p_name:
        :param delay:
        :return:
        """
        if p_name and p_name in self._p_tunnel_cursor:
            msg_data = self._p_tunnel_cursor[p_name].get_msg(delay)
            return msg_data


class MsgTunnel:
    """
    消息隧道
    """
    __queue = {}
    __k_queue = []

    def __init__(self, p_name):
        self._p_name = p_name

    def __str__(self):
        return str(id(self))

    def recv_msg(self, msg):
        try:
            # 发送消息
            msg_mark = get_msg_mark()
            if not os.path.exists(msg_pool + self._p_name):
                os.mkdir(msg_pool + self._p_name)
            with open(msg_pool + self._p_name + '/' + msg_mark, 'w') as file:
                json.dump(msg, file, ensure_ascii=False)
        except Exception as e:
            raise Exception('无法识别的消息类型,原因: %s' % (e))

    def insert_msg(self, tag):
        """
        装载消息
        :param tag:
        :return:
        """
        self.__k_queue.clear()
        for root, dirs, files in os.walk(msg_pool + tag):
            for name in files:
                file_path = os.path.join(root, name)
                with open(file_path, 'r') as file:
                    try:
                        # 尝试以json形式读取
                        new_kwargs = json.load(file)
                    except Exception as e:
                        # 失败后以二进制形式读取
                        new_kwargs = file.readline()
                    # 加载消息
                    self.__queue[name] = {
                        'msg': new_kwargs,
                        'file_path': file_path
                    }
        self.__k_queue = list(self.__queue.keys())

    def query_msg(
            self,
            delay: int
    ):
        """
        查询隧道信息
        :return:
        """
        msg_data = 'none'
        while True:
            time.sleep(delay)
            if self.__k_queue:
                # 获取信息
                msg_k = self.__k_queue.pop(0)
                msg_obj = self.__queue.pop(msg_k)
                __r_file_path = re.sub('\\\\', '/', msg_obj['file_path'])
                try:
                    # 消息消费成功
                    with open(__r_file_path, 'r') as file:
                        msg_data = eval(file.readline())
                except FileNotFoundError as fne:
                    print(fne)
                    pass
                except Exception as e:
                    print('e', e)
                else:
                    # 清除消息
                    os.remove(__r_file_path)
                    return msg_data
            self.insert_msg(self._p_name)


class SocketMsgTunnel(MsgTunnel):
    def __init__(self, p_name: str):
        super(SocketMsgTunnel, self).__init__(p_name)
        self._p_name = p_name

    def send_msg(self, msg):
        """
        发送消息
        :param msg:
        :return:
        """
        bound_dict = bone_data.get_send_data(self._p_name, get_msg_mark(), msg, '1232333123123')
        flag = True
        msg_answer = ''
        while flag:
            # 实例内部套接字初始化
            __socket = get_socket()
            logger.info(str(__socket.recv(1024), encoding='utf-8'))
            try:
                # 尝试发送消息
                if not __socket.sendall(bytes(json.dumps(bound_dict), encoding="utf-8")):
                    while flag:
                        msg_answer = json.loads(str(__socket.recv(1024), encoding='utf-8'), encoding='utf-8')
                        logger.info('发送成功')
                        flag = False
            except Exception as e:
                print('发送失败', msg, '原因', e)
                raise e
            __socket.close()
        return msg_answer

    def get_msg(self, delay: int):
        """
        获取消息()
        :return:
        """
        # 实例内部套接字初始化
        __socket = get_socket()
        logger.info(str(__socket.recv(1024), encoding='utf-8'))
        p_name = self._p_name
        flag = True
        msg = ''
        msg_body = ''
        while flag:
            time.sleep(delay)
            try:
                __socket.sendall(bytes(str([p_name]), encoding='utf-8'))
                recv_str = str(__socket.recv(1024), encoding='utf-8')
                if recv_str == 'none':
                    return recv_str
                msg = eval(recv_str)
            except Exception as e:
                err_msg = {
                    'ack_code': '500',
                    'ack_msg': str(e)
                }
                __socket.sendall(bytes(encode_ack_info(err_msg), encoding='utf-8'))
            else:
                if isinstance(msg, dict):
                    # 发送消息接受确认
                    msg_mark = list(msg.keys())[0]
                    msg_body = msg[msg_mark]
                    __socket.sendall(bytes(encode_ack_info({
                        'ack_code': '200',
                        'ack_mark': msg_mark
                    }), encoding='utf-8'))
                flag = False
        __socket.close()
        return msg_body['msg']
