# -*- coding: utf-8 -*-

from __future__ import print_function

import errno
import socket
import ssl
import struct
import logging
import threading
import time
import traceback

import msgpack

_global_sender = None

LOGGER = logging.getLogger('mona-logger')

_exceptions_logged = 0
MAX_EXCEPTIONS_TO_LOG = 5


def _set_global_sender(sender):  # pragma: no cover
    """ [For testing] Function to set global sender directly
    """
    global _global_sender
    _global_sender = sender


def setup(tag, **kwargs):  # pragma: no cover
    global _global_sender
    _global_sender = FluentSender(tag, **kwargs)


def get_global_sender():  # pragma: no cover
    return _global_sender


def close():  # pragma: no cover
    get_global_sender().close()


class EventTime(msgpack.ExtType):
    def __new__(cls, timestamp):
        seconds = int(timestamp)
        nanoseconds = int(timestamp % 1 * 10**9)
        return super(EventTime, cls).__new__(
            cls,
            code=0,
            data=struct.pack(">II", seconds, nanoseconds),
        )


class FluentSender(object):
    def __init__(self,
                 tag,
                 host='localhost',
                 port=24224,
                 bufmax=1 * 1024 * 1024,
                 timeout=3.0,
                 verbose=False,
                 buffer_overflow_handler=None,
                 nanosecond_precision=False,
                 msgpack_kwargs=None,
                 use_ssl=False,
                 ssl_context_args={},
                 ssl_server_hostname="",
                 **kwargs):
        """
        :param kwargs: This kwargs argument is not used in __init__. This will be removed in the next major version.
        """
        self.tag = tag
        self.host = host
        self.port = port
        self.bufmax = bufmax
        self.timeout = timeout
        self.verbose = verbose
        self.buffer_overflow_handler = buffer_overflow_handler
        self.nanosecond_precision = nanosecond_precision
        self.msgpack_kwargs = {} if msgpack_kwargs is None else msgpack_kwargs
        self.ssl = use_ssl
        self.ssl_context_args = ssl_context_args
        self.ssl_server_hostname = ssl_server_hostname

        self.socket = None
        self.pendings = None
        self.lock = threading.Lock()
        self._closed = False
        self._last_error_threadlocal = threading.local()

    def emit(self, label, data):
        if self.nanosecond_precision:
            cur_time = EventTime(time.time())
        else:
            cur_time = int(time.time())
        return self.emit_with_time(label, cur_time, data)

    def emit_with_time(self, label, timestamp, data):
        if self.nanosecond_precision and isinstance(timestamp, float):
            timestamp = EventTime(timestamp)
        try:
            bytes_ = self._make_packet(label, timestamp, data)
        except Exception as e:
            self.last_error = e
            bytes_ = self._make_packet(
                label, timestamp, {
                    "level": "CRITICAL",
                    "message": "Can't output to log",
                    "traceback": traceback.format_exc()
                })
        return self._send(bytes_)

    @property
    def last_error(self):
        return getattr(self._last_error_threadlocal, 'exception', None)

    @last_error.setter
    def last_error(self, err):
        self._last_error_threadlocal.exception = err

    def clear_last_error(self, _thread_id=None):
        if hasattr(self._last_error_threadlocal, 'exception'):
            delattr(self._last_error_threadlocal, 'exception')

    def close(self):
        with self.lock:
            if self._closed:
                return
            self._closed = True
            if self.pendings:
                try:
                    self._send_data(self.pendings)
                except Exception:
                    self._call_buffer_overflow_handler(self.pendings)

            self._close()
            self.pendings = None

    def _make_packet(self, label, timestamp, data):
        if label:
            tag = '.'.join((self.tag, label))
        else:
            tag = self.tag
        packet = (tag, timestamp, data)
        if self.verbose:
            print(packet)
        return msgpack.packb(packet, **self.msgpack_kwargs)

    def _send(self, bytes_):
        with self.lock:
            if self._closed:
                return False
            return self._send_internal(bytes_)

    def _send_internal(self, bytes_):
        # buffering
        if self.pendings:
            self.pendings += bytes_
            bytes_ = self.pendings

        try:
            self._send_data(bytes_)

            # send finished
            self.pendings = None

            return True
        except socket.error as e:
            LOGGER.debug("Error while sending data: {}".format(str(e)))
            self.last_error = e

            # close socket
            self._close()

            # clear buffer if it exceeds max buffer size
            if self.pendings and (len(self.pendings) > self.bufmax):
                self._call_buffer_overflow_handler(self.pendings)
                self.pendings = None
            else:
                self.pendings = bytes_

            return False

    def _check_recv_side(self):
        try:
            self.socket.settimeout(0.0)
            try:
                recvd = self.socket.recv(4096)
            except socket.error as recv_e:
                if recv_e.errno not in [errno.EWOULDBLOCK, errno.ENOENT]:
                    raise
                return

            if recvd == b'':
                raise socket.error(errno.EPIPE, "Broken pipe")
        finally:
            self.socket.settimeout(self.timeout)

    def _send_data(self, bytes_):
        # reconnect if possible
        self._reconnect()
        # send message
        bytes_to_send = len(bytes_)
        bytes_sent = 0
        self._check_recv_side()
        while bytes_sent < bytes_to_send:
            sent = self.socket.send(bytes_[bytes_sent:])
            if sent == 0:
                raise socket.error(errno.EPIPE, "Broken pipe")
            LOGGER.debug("Sent {} bytes".format(str(sent)))
            bytes_sent += sent
        self._check_recv_side()

    def _wrap_sock_with_ssl(self, sock):
        if not self.ssl:
            return sock

        context = ssl.create_default_context(**self.ssl_context_args)
        return context.wrap_socket(
            sock, server_hostname=self.ssl_server_hostname)

    def _reconnect(self):
        if not self.socket:
            try:
                if self.host.startswith('unix://'):
                    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
                    sock = self._wrap_sock_with_ssl(sock)
                    sock.settimeout(self.timeout)
                    sock.connect(self.host[len('unix://'):])
                else:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock = self._wrap_sock_with_ssl(sock)
                    sock.settimeout(self.timeout)
                    # This might be controversial and may need to be removed
                    sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
                    sock.connect((self.host, self.port))
            except Exception as e:
                global _exceptions_logged
                if _exceptions_logged < MAX_EXCEPTIONS_TO_LOG:
                    LOGGER.debug(
                        "Exception while connecting to socket: {}".format(
                            str(e)))
                    _exceptions_logged += 1
                try:
                    sock.close()
                except Exception:  # pragma: no cover
                    pass
                raise e
            else:
                self.socket = sock
                LOGGER.debug("Socket object: {}".format(str(sock)))

    def _call_buffer_overflow_handler(self, pending_events):
        try:
            if self.buffer_overflow_handler:
                self.buffer_overflow_handler(pending_events)
        except Exception as e:
            # User should care any exception in handler
            pass

    def _close(self):
        try:
            sock = self.socket
            if sock:
                try:
                    try:
                        sock.shutdown(socket.SHUT_RDWR)
                    except socket.error:  # pragma: no cover
                        pass
                finally:
                    try:
                        sock.close()
                    except socket.error:  # pragma: no cover
                        pass
        finally:
            self.socket = None

    def __enter__(self):
        return self

    def __exit__(self, typ, value, traceback):
        try:
            self.close()
        except Exception as e:  # pragma: no cover
            self.last_error = e
