"""
:copyright: (c) 2017 by Jumper Labs Ltd.
:license: Apache 2.0, see LICENSE.txt for more details.
"""
import os
import os.path
import array
from time import sleep
from threading import Thread, Lock
import socket
import errno
import socket
import json
import struct
import logging
import sys

from .timeout_dec import timeout
from .common import TimeoutException
from common import WrongStateError



class JemuUartTcp(object):
    """
    Represents a UART device.
    """
    # uart_port = 0
    def __init__(self, vlab):
        self._buffer = b''
        self._vlab = vlab
        # self._read_from_uart_thread = None
        self._lock = Lock()
        # self._print_to_screen = False
        # self._should_close_thread = False

        self._addr = "localhost"
        self._conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._conn.settimeout(0.3)
        self._callbacks = []
        self._thread = None
        self._should_run = False
        self._connection_closed = True
        self._threads = []

    # def print_uart_to_screen(self):
    #     self._print_to_screen = True

    def open(self):
        self._should_run = True
        t = Thread(target=self._connection_task)
        self._threads.append(t)
        t.start()

        @timeout(6)
        def wait_for_connection():
            while self._uart_port == 0:
                sleep(0.1)

            while not self._connect():
                sleep(0.1)
        try:
            wait_for_connection()
        except TimeoutException:
            self._vlab.stop()
            raise Exception("Error: Couldn't connect to Emulator. Please contact us at support@jumper.io with a copy of this trace text port: " + self._uart_port)

    def remove(self):
        pass

    def _connect(self):
        result = False

        try:
            self._conn.connect((self._addr, int(self._uart_port)))
            self._connection_closed = False
            result = True
        except Exception:
            self._conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        finally:
            return result

    def close(self):
        self._should_run = False
        for t in self._threads:
            t.join()

    def _connection_task(self):
        while self._should_run:
            try:
                new_data = self._conn.recv(1024)
                if new_data == '':
                    break

                # sys.stdout.write(new_data)
                
                with self._lock:
                    self._buffer += new_data
            except socket.timeout:
                continue
            except socket.error as e:
                self._connection_closed = True
                return None

        if not self._connection_closed:
            self._conn.close()
            self._connection_closed = True
   
    def read_line(self, line_separator=b'\r\n'):
        """
        Reads a single line from UART.

        :param line_separator: Substring for separating lines. Usually b'\\\\r\\\\n' or b'\\\\n'

        :return: A byte string of data read from the device, including line_separator
        """
        while line_separator not in self._buffer:
            sleep(0.2)
        with self._lock:
            line_length = self._buffer.find(line_separator) + len(line_separator)
            data = self._buffer[:line_length]
            self._buffer = self._buffer[line_length:]
        return data

    def read(self):
        """

        :return: data available on the UART device. Returns an empty bytes string if no data is available.
        """
        with self._lock:
            data = self._buffer
            self._buffer = b''
        return data

    def wait_until_uart_receives(self, data, timeout=None):
        """
        Blocks until specified data is received on UART.
        If the device is paused, this function will continue the execution and will pause the device when the data is ready or timeout occured.
        If the device is running, the function will not pause the device.

        :param data: Expected bytes string.
        :param timeout: Emulation time specified in milliseconds. jumper.vlab.TimeoutException is raised if timeout occurred before data was available in the buffer.
        :return: The data available on in the UART buffer when the specified data was received. Note that this can be more than the data provided in the data parameter.
        """
        original_state = self._vlab.get_state()

        if original_state == 'running':
            self._vlab.pause()
        elif original_state != 'paused':
            raise WrongStateError('state should be paused or running but was {}'.format(original_state))

        if timeout is not None:
            self._vlab.stop_after_ms(timeout)

        self._vlab.resume()

        while data not in self._buffer and self._vlab.get_state() == 'running':
            sleep(0.2)

        if timeout is not None:
            self._vlab.cancel_stop()

        if original_state == 'running':
            self._vlab.resume()
        elif original_state == 'paused':
            self._vlab.pause()
        with self._lock:
            if data in self._buffer:
                tmp = self._buffer
                self._buffer = b''
                return tmp

        raise TimeoutException("timeout while waiting for data from uart")

    def write(self, data):
        self._conn.sendall(data)
