import socket
import threading
import json
import os

DESTINATION = {"Commander": 1, "Coordinator": 2, "VersionProxy": 3}

_serial = 0


def init_common(cmd, hash=0, priority=0, pid=os.getpid(), user=""):
    return Common(**{"hash": hash, "cmd": cmd, "priority": priority,
                     "pid": pid, "user": user})


def get_packet(des, cmd, data):
    common = init_common(cmd)
    return json.dumps({'TYPE': des, 'COMMON': common.get_json(),
                       'DATA': json.dumps(data)}), common.get_serial()


class Common():
    """docstring for Common()"""

    def __init__(self, **kwds):
        self.kwds = kwds
        self.kwds.setdefault("hash", 0)
        self.kwds.setdefault("pid", os.getpid())
        self.kwds.setdefault("user", "")
        self.kwds.setdefault("priority", 0)
        self.kwds.setdefault("version", 0)
        self.kwds.setdefault("ignoreIdle", False)
        self.kwds.setdefault("ignorePreempted", False)

    def _get_serial(self):
        global _serial
        _serial += 1
        return _serial

    def get_serial(self):
        return self.kwds['serial']

    def get_json(self):
        self.kwds["serial"] = self._get_serial()
        return json.dumps(self.kwds)


class _intercomm():
    """docstring for _intercomm"""

    def __init__(self, destination, timeout=2):
        self.destination = destination
        self.timeout = timeout
        self.ss = socket.create_connection(destination, timeout)
        self.sr = socket.create_connection(destination)
        self.tr = threading.Thread(target=self.recv_message, args=(self.sr,))
        self.tr.setDaemon(True)
        self.tr.start()

    def send_message(self, packet):
        print('send message...')
        self.ss.sendall(packet.encode(encoding='utf-8'))
        self.ss.sendall('\n'.encode(encoding='utf-8'))
        print('send message Done')

    def recv_message(self, *args):
        sr = args[0]
        print('ready receive message from', sr)
        while True:
            received = sr.recv(1024)
            if not received:
                break
            s = received.decode('utf-8', errors='replace')
            print('Recv:', s)
        print('receive message Done')

    def release(self):
        self.ss.close()
        self.sr.close()
