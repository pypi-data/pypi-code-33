# -*- coding: utf8 -*-
import threading

import argparse
import asyncore
import datetime
import errno
import json
import logging
import os
import signal
import socket
import struct
import subprocess
import sys
import time
from contextlib import closing

import requests
from requests import RequestException

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S')


def setup_logging(log_file):
    logging.basicConfig()

    new_logger = logging.getLogger('log_monitor')
    new_logger.setLevel(logging.DEBUG)
    new_logger.propagate = False

    formatter = logging.Formatter('%(asctime)s.%(msecs)03d %(name)s %(levelname)s %(message)s', '%Y-%m-%d %H:%M:%S')

    if log_file is not None:
        ch2 = logging.FileHandler(log_file)
        ch2.setLevel(logging.DEBUG)
        ch2.setFormatter(formatter)
        new_logger.addHandler(ch2)
    else:
        new_logger.addHandler(logging.NullHandler())

    return new_logger


logger = setup_logging(os.environ.get('ML_LOG_MONITOR_LOG_FILE'))


class PerpetualTimer(object):
    def __init__(self, interval, function):
        self._interval = interval
        self._function = function
        self._thread = threading.Timer(self._interval, self.handle_function)

    def handle_function(self):
        self._function()
        self._thread = threading.Timer(min(0., self._interval), self.handle_function)
        self._thread.start()

    def start(self):
        self._thread.start()

    def cancel(self):
        self._thread.cancel()


# noinspection PyClassicStyleClass
class DataHandler:
    max_saved_items = 1000
    max_batch_send = 50
    send_every_x_seconds = 5

    def __init__(self, endpoint, session=None):
        self._pending_data = None
        self._endpoint = endpoint

        headers = {'Content-type': 'application/json'}

        session = session or requests.session()
        session.headers.update(headers)

        self._session = session if endpoint is not None else None
        self._unhandled_exception = False
        self._exception_stack_trace = ''
        self._items = []
        self._sending_thread_lock = threading.Lock()
        self._sending_thread = None

    def close(self):
        if self._sending_thread is not None:
            self._sending_thread.cancel()

        self._send_all_items()

        if self._sending_thread is not None:
            self._sending_thread.cancel()

    def _send_all_items(self):
        self._send_items(send_all_items=True)

    def __batch_send_items(self):
        if len(self._items) > self.max_saved_items:
            self._items = self._items[-self.max_saved_items:]

        total_send = min(len(self._items), self.max_batch_send)

        r = self._session.post(self._endpoint, data=json.dumps(self._items[0:total_send]))
        self._items = self._items[total_send:]
        try:
            r.raise_for_status()
        except RequestException:
            pass

    def _send_items(self, send_all_items=False):
        with self._sending_thread_lock:
            while True:
                if not self._items:
                    return

                self.__batch_send_items()

                if not send_all_items:
                    break

    def post_json(self, data):
        with self._sending_thread_lock:
            self._items.append(data)

            if self._sending_thread is None:
                self._sending_thread = PerpetualTimer(self.send_every_x_seconds, self._send_items)
                self._sending_thread.start()

    def on_line(self, line):
        try:
            data = json.loads(line)
        except ValueError:
            return

        if data.get('category') == 'unhandled':
            self._unhandled_exception = True

            message = data.get('message')

            if message is not None:
                self._exception_stack_trace += message

        if self._session is not None:
            self.post_json(data)

    def process_text(self, text):
        if not text:
            return

        lines = text.split('\n')

        for i, line in enumerate(lines):
            if self._pending_data is not None:
                line = self._pending_data + line
                self._pending_data = None

            if i == len(lines) - 1:  # last or first (and only one)
                if len(line) == 0 or text[-1] != '\n':
                    self._pending_data = line
                    continue

            self.on_line(line)


# noinspection PyClassicStyleClass
class IncomingDataHandler(asyncore.dispatcher):
    def __init__(self, port, endpoint, data_handler=None):
        asyncore.dispatcher.__init__(self)

        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connect(('', port))
        self.data_handler = data_handler or DataHandler(endpoint)
        self.closed_by_application = False

    def writable(self):
        return False

    def close(self):
        asyncore.dispatcher.close(self)

        if self.data_handler is not None:
            self.data_handler.close()

    def read_at_least(self, size, wait_for_data):
        data = b''

        while len(data) < size:
            try:
                current_data = self.recv(size)
                data += current_data
            except socket.error as why:
                if why.errno == errno.EAGAIN:
                    if wait_for_data:
                        time.sleep(0.1)
                        continue
                    else:
                        return data

                raise

            if len(data) == 0:
                return data

        return data

    def handle_read(self):
        total_read = 0
        logger.info('handle_read begin')

        data = self.read_at_least(4, wait_for_data=False)
        if len(data) > 0:
            size = struct.unpack('!i', data[:4])[0]

            if size == 0:  # the application sent zero size in order to close this
                logger.info('closed_by_application: True')
                self.closed_by_application = True
                self.close()
            elif size > 0:  # the application sent zero size in order to close this
                data = self.read_at_least(size, wait_for_data=True)

                current_block = data.decode('utf8')

                total_read += 4 + size

                self.data_handler.process_text(current_block)

        logger.info('handle_read end %s', total_read)

        return total_read

    def handle_close(self):
        logger.info('socket closed')
        self.close()
        self.data_handler.close()


class App(object):
    def __init__(self, sys_args=None):
        args = self._create_args_parser(sys_args)

        if not args.isRoot:
            if sys_args is not None:
                sys_args = [__file__] + sys_args

            restart_params = sys_args[:] if sys_args else sys.argv[:]
            restart_params += [self.root_param_name()]

            restart_params = [sys.executable] + restart_params

            self._restart(restart_params)

        self.args = args

    @classmethod
    def _create_args_parser(cls, sys_args):
        parser = argparse.ArgumentParser(description='listen socket for logs.')
        parser.add_argument('--port', type=int, required=True)
        parser.add_argument('--endpoint', required=True)
        parser.add_argument('--terminateEndpoint')
        parser.add_argument(cls.root_param_name(), action='store_true')

        return parser.parse_args(sys_args)

    @classmethod
    def root_param_name(cls):
        return '--isRoot'

    @classmethod
    def _restart(cls, restart_params):
        subprocess.Popen(restart_params)
        sys.exit(0)

    def _post_terminate(self, unhandled_exception, ctrl_c=False, exception_stack_trace=None):
        if not self.args.terminateEndpoint:
            logger.info('post_terminate skipped (no --terminateEndpoint)')
            return

        logger.info('post_terminate unhandled_exception: %s ctrl_c: %s', unhandled_exception, ctrl_c)

        headers = {'content-type': 'application/json'}
        body = {
            'ts': datetime.datetime.utcnow().isoformat(),
            'ctrl_c': ctrl_c,
            'unhandled_exception': unhandled_exception,
            'exception_stack_trace': exception_stack_trace,
        }
        data = json.dumps(body)

        requests.post(self.args.terminateEndpoint, data=data, headers=headers)

    # noinspection PyUnusedLocal
    def _signal_handler(self, current_signal, frame):
        logger.info('signal', current_signal)
        self._post_terminate(unhandled_exception=False, ctrl_c=True)
        sys.exit(0)

    def main(self):
        signal.signal(signal.SIGINT, self._signal_handler)  # ctrl-c from console

        logger.info('log monitor started on pid %s', os.getpid())

        with closing(IncomingDataHandler(self.args.port, self.args.endpoint)) as handler:
            asyncore.loop()

            logger.info('asyncore exit')

            closed_by_ctrl_c = not handler.closed_by_application

            self._post_terminate(unhandled_exception=handler.data_handler._unhandled_exception, ctrl_c=closed_by_ctrl_c,
                                 exception_stack_trace=handler.data_handler._exception_stack_trace)


if __name__ == "__main__":  # pragma: no cover
    # noinspection PyBroadException
    try:
        app = App()
        app.main()
    except Exception as ex:
        if ex is not SystemExit:
            logger.exception('exit log monitor')
