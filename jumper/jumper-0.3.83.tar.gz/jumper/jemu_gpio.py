"""
:copyright: (c) 2017 by Jumper Labs Ltd.
:license: Apache 2.0, see LICENSE.txt for more details.
"""
from threading import Lock
from common import JemuConnectionException


class JemuGpio:
    _PIN_NUM = "pin_number"
    _TRANSITION_TYPE = "transition_type"
    _DESCRIPTION = "description"
    _PIN_LEVEL_EVENT = "pin_level_event"
    _DEVICE_TIME = "device_time"

    def __init__(self, sudo):
        self._pin_level_callback = None
        self._jemu_socket_manager = None
        self._lock = Lock()
        self._sudo = sudo

    def on_pin_level_event(self, callback):
        with self._lock:
            self._pin_level_callback = callback

    def receive_packet(self, jemu_packet):
        if jemu_packet[self._DESCRIPTION] == self._PIN_LEVEL_EVENT:
            with self._lock:
                if self._pin_level_callback:
                    try:
                        self._pin_level_callback(
                            jemu_packet[self._PIN_NUM],
                            jemu_packet[self._TRANSITION_TYPE],
                            jemu_packet[self._DEVICE_TIME]
                        )
                    except TypeError:
                        self._pin_level_callback(jemu_packet[self._PIN_NUM], jemu_packet[self._TRANSITION_TYPE])

    def set_connection_manager(self, jemu_socket_manager):
        self._jemu_socket_manager = jemu_socket_manager
        self._jemu_socket_manager.register(self.receive_packet)

    def get_pin_level(self, pin_num):
        return self._sudo.get_pin_level(pin_num)

    def set_pin_level(self, pin_num, pin_level):
        return self._sudo.set_pin_level(pin_num, pin_level)
