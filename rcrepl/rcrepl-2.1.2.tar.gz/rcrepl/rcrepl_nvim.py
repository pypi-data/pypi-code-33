import sys
import socket
import json
import os
import time
import tempfile
from .rcrepl_vim import build_error_list
try:
    from pynvim import attach, NvimError
except ImportError:
    print("You need 'neovim' python library to run this adapter. Please install it using pip")

def get_nvim():
    return attach('socket', path=get_nvim_address())

def main():
    port = int(os.environ['RCREPL_PORT'])
    nvim = get_nvim()
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    client_socket.connect(('0.0.0.0', port))
    client_socket.sendall("-- editor neovim".encode('utf-8'))
    msg = bytes()
    while True:
        a = client_socket.recv(1024)
        msg = msg + a
        try:
            v = json.loads(msg.decode())
            msg = bytes()
            process_message(v, nvim)
        except json.decoder.JSONDecodeError as v:
            pass

def exception(e):
    print("There was an error : {} - {}".format(e.__class__.__name__, e))
    raise e

def get_nvim_address():
    return os.environ['NVIM_LISTEN_ADDRESS']

def call_vim_function(fnc, nvim):
        try:
            nvim.call(fnc)
        except NvimError as e:
            print("Warning: No function {} defined in Neovim.".format(fnc))

def process_message(msg, nvim):
    if msg['op'] == 'indicate_activity':
        call_vim_function('RCREPLIndicateActivity', nvim)
    elif msg['op'] == 'status_update':
        try:
            elist = build_error_list(msg['data']['status'])
            nvim.call('setqflist', [], 'r', {"items": elist, "title": "RCREPL Error list"})
            if len(msg['data']['status']['errors']) > 0:
                call_vim_function('RCREPLIndicateError', nvim)
            elif len(msg['data']['status']['warnings']) > 0:
                call_vim_function('RCREPLIndicateWarnings', nvim)
            else:
                call_vim_function('RCREPLIndicateSuccess', nvim)
        except Exception as v:
            exception(v)

if __name__ == "__main__":
    main()
