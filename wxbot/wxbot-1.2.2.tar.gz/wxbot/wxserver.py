# -*- coding:utf-8 -*-
__authon__ = "cfn@leapy.cn"

import socket
import sys
from wxbot import wxmessage

class mysocket(wxmessage.message):

    def __init__(self,host,port):
        wxmessage.message.__init__(self)
        self.host = host
        self.port = int(port)
        self.numListen = 1
        self.sock = ""
        pass

    # 打开socket
    def open(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.host, self.port))
        self.sock.listen(self.numListen)
        pass

    # 停止socket
    def stop(self):
        if self.sock:
            self.sock.close()
        pass

    # 运行
    def run(self):
        try:
            self.open()
        except Exception as E:
            self.error("开启scoket失败：", E)
        else:
            self.success('已在 %s 的 %s 端口开启服务' % (self.host, self.port))
            while True:
                try:
                    sock, addr = self.sock.accept()
                except Exception as e:
                    self.error('在连接客户端时出错：', e)
                else:
                    self.onAccept(sock, addr)

    # 接入客户端
    def onAccept(self, sock, addr):
        sock.settimeout(10.0)
        if self.sock:
            try:
                data = sock.recv(8192)
            except socket.error as e:
                self.error('在接收来自 %s:%s 的数据时出错：，%s' % (addr[0], addr[1], e))
                self.stop()
            else:
                if data == b'#STOP#':
                    self.notice('%s:%s 已停止' % (self.host,self.port))
                    self.stop()
                    sys.exit(0)
                else:
                    print(addr)
                    print(data)
                    pass
        pass


if __name__ == "__main__":
    mysocket("0.0.0.0","8088").run()