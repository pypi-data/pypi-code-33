#!/usr/bin/python
# -*- coding: utf-8 -*-
import socket
import traceback
from thread import start_new_thread

from constants import END_OF_MESSAGE
from db_utils import get_database_con

SPEAKER_HOST = ''
SPEAKER_PORT = 7888

def smart_speaker_loop():
    while(True):
        start_server_socket()
    return

def clientthread(conn):
    return


def listen_for_requests(s):
    # wait to accept a connection - blocking call
    conn, addr = s.accept()
    print('Connected with ' + addr[0] + ':' + str(addr[1]))

    # start new thread takes 1st argument as a function name to be run, second is the tuple of arguments to the function.
    start_new_thread(clientthread, (conn,))

def start_server_socket():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print('Socket created')

    # send_notification_to_users(['sascha'], "Titel", "Nachricht", get_database_con())

    # Bind socket to local host and port
    try:
        s.bind((SPEAKER_HOST, SPEAKER_PORT))
    except socket.error as msg:
        traceback.print_exc()
        print('Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1])

    print('Socket bind complete')

    # Start listening on socket
    s.listen(10)
    print('Socket now listening')

    while 1:
        try:
            listen_for_requests(s)
        except:
            traceback.print_exc()
            break

    s.close()