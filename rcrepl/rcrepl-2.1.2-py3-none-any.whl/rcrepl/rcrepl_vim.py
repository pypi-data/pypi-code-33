import sys
import socket
import json
import os
import time
import threading

def main():
    port = int(os.environ['RCREPL_PORT'])
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    client_socket.connect(('0.0.0.0', port))
    client_socket.sendall("-- editor vim".encode('utf-8'))
    vimconnector = VimConnector()
    msg = bytes()
    while True:
        a = client_socket.recv(1024)
        msg = msg + a
        try:
            v = json.loads(msg.decode())
            msg = bytes()
            process_message(v, vimconnector)
        except json.decoder.JSONDecodeError as v:
            pass

def exception(e):
    print("There was an error : {} - {}".format(e.__class__.__name__, e))

class VimConnector:
    def __init__(self):
        serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        serversocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        serversocket.bind(('127.0.0.1', 0))
        self.socket = serversocket
        self.connectedSocket = None
        self.thread = threading.Thread(target=self.thread_callback, args=[self.socket], daemon=True)
        self.thread.start()
        self.connect_to_vim()

    def thread_callback(self, socket):
        self.socket.listen(1)
        while True:
            (clientsocket, _) = self.socket.accept()
            self.connectedSocket = clientsocket
            print("Connected to vim instance from socket : {}".format(self.connectedSocket.getsockname()[1]))

    def get_vim_address(self):
        return os.environ['VIM_SERVERNAME']

    def connect_to_vim(self):
        vim_server = self.get_vim_address()
        ip = self.socket.getsockname()[1]
        cmd = "vim --servername {} --remote-expr \"execute('let chan = ch_open(\\\"localhost:{}\\\", {{\\\"mode\\\":\\\"json\\\"}})')\"".format(vim_server, ip)
        # ^^^ In the above expression, the "let chan =" part is essential. If left out, it appears that the channel is garbage collected (or something)
        # and though the channel recieves messages, it seem to simply drop them, instead of executing the contained commands.
        os.system(cmd)

    def call_vim_function(self, func, args):
        self.connectedSocket.sendall(json.dumps(["call", func, args]).encode('utf-8'))
        self.connectedSocket.sendall(json.dumps(["redraw", ""]).encode('utf-8'))

def build_error_list(items):
    ret = []
    for (idx, e) in enumerate(items['errors']):
        for (idx1, ln) in enumerate(e['text'].split('\n')):
            # We attach each line to the error, keeping the error no (nr) same for the
            # lines belonging to same error.
            if idx1 == 0:
                ret.append({'filename': e['file_name'], 'lnum': e['line'], 'col': e['column'], 'text': ln, 'nr': idx, 'type': 'E'})
            else:
                ret.append({'text': ln, 'nr': idx, 'type': 'E'})

    for (idx, e) in enumerate(items['warnings']):
        for (idx1, ln) in enumerate(e['text'].split('\n')):
            if idx1 == 0:
                ret.append({'filename': e['file_name'], 'lnum': e['line'], 'col': e['column'], 'text': ln, 'nr': idx, 'type': 'W'})
            else:
                ret.append({'text': ln, 'nr': idx, 'type': 'W'})
    return ret

def process_message(msg, vimc):
    if msg['op'] == 'indicate_activity':
        vimc.call_vim_function('RCREPLIndicateActivity', [])
    elif msg['op'] == 'status_update':
        try:
            elist = build_error_list(msg['data']['status'])
            vimc.call_vim_function('setqflist', [[], 'r', {"items": elist, "title": "RCREPL Error list"}])
            if len(msg['data']['status']['errors']) > 0:
                vimc.call_vim_function('RCREPLIndicateError', [])
            elif len(msg['data']['status']['warnings']) > 0:
                vimc.call_vim_function('RCREPLIndicateWarnings', [])
            else:
                vimc.call_vim_function('RCREPLIndicateSuccess', [])
        except Exception as v:
            exception(v)

if __name__ == "__main__":
    main()
