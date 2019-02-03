"""
:copyright: (c) 2017 by Jumper Labs Ltd.
:license: Apache 2.0, see LICENSE.txt for more details.
"""

import logging
import sys
from jemu_mem_peripheral import JemuMemPeripheral
import threading
from common import JemuConnectionException, WrongStateError


class JemuSudo(JemuMemPeripheral):
    _jemu_connection = None
    _peripheral_type = None
    _state = None

    _DESCRIPTION = "description"
    _STOP_AFTER_COMMAND = "stop_after"
    _START_COMMAND = "resume_running"
    _COMMAND = "command"
    _NANO_SECONDS = "nanoseconds"
    _TYPE_STRING = "type"
    _PERIPHERAL_ID = "peripheral_id"
    _PERIPHERAL_TYPE = "peripheral_type"
    _STOPPED = "stopped"
    _RESUMED = "resumed"
    _COMMAND_SET_TIMER = "set_timer"
    _MESSAGE_ID = "message_id"
    _GET_STATE_COMMAND = "get_state"
    _CANCEL_STOP_ON_TICK = "cancel_stop"
    _CANCEL_STOP_RESPONSE = "stop_canceled"
    _GET_DEVICE_TIME = "get_device_time"
    _VALUE = "value"
    _TIMER_ID = "timer_id"
    _EMULATOR_STATE = "emulator_state"
    _DEVICE_TIME = "device_time"
    _SUDO_EXIT = "sudo_exit"
    _SP_MAX = "sp_max"
    _CODE_COVERAGE = "code_coverage"
    _TERMINATE = "terminate"
    _PAUSE_COMMAND = "pause"
    _PIN_NUM = "pin_number"
    _TRANSITION_TYPE = "transition_type"
    _PIN_LEVEL_EVENT = "pin_level_event"
    _PIN_LEVEL = "pin_level"
    _PIN_NUMBER = "pin_number"
    _GET_PIN_LEVEL = "get_pin_level"
    _SET_PIN_LEVEL = "set_pin_level"
    _VALUE_RESPONSE = "value_response"
    _TICKS = "ticks"

    _LOG_LEVEL = logging.ERROR

    def __init__(self, jemu_connection, name, peripheral_type, gdb_mode):
        JemuMemPeripheral.__init__(self, jemu_connection, name, peripheral_type, None)
        self._gdb_mode = gdb_mode
        self._peripheral_type = peripheral_type
        self._jemu_connection = jemu_connection
        self._jemu_connection.register(self._receive_packet)
        self._timer_id_callback_dict = {}
        self._device_time_lock = threading.RLock()
        self._device_time = None
        self._stopped_packet_received = threading.Event()
        self._exit_code = None
        self._on_sp_max = None
        self._on_code_coverage = None
        self._logger = logging.getLogger('JemuSudo')
        log_handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        log_handler.setFormatter(formatter)
        self._logger.addHandler(log_handler)
        self._logger.setLevel(self._LOG_LEVEL)
        log_handler.setLevel(self._LOG_LEVEL)
        self._timers_lock = threading.Lock()
        self._name = name

    def _generate_json_command(self, command):
        return {
            self._COMMAND: command,
        }

    def stop_after_ns(self, nanoseconds):
        self._logger.debug('stop after')
        json_command = self._generate_json_command(self._STOP_AFTER_COMMAND)
        json_command[self._NANO_SECONDS] = nanoseconds
        self._jemu_connection.send_command(json_command, self._name, self._peripheral_type)

    def run_for_ns(self, nanoseconds):

        if self.get_state() == 'running':
            self.pause()

        timer_event = threading.Event()

        def timer_callback():
            self._logger.debug('Timer callback inside run_for_ns')
            timer_event.set()

        ticks = self.set_timer(nanoseconds, timer_callback)
        if ticks != 0:
            self.resume()
        timer_event.wait()

    def pause(self):
        if self.get_state() == 'paused':
            return
        self._logger.debug('pause')


        response = self._jemu_connection.send_command(
            self._generate_json_command(self._PAUSE_COMMAND), self._name, self._peripheral_type
        )
        if not (self._DESCRIPTION in response and
                response[self._DESCRIPTION] == self._EMULATOR_STATE and
                self._VALUE in response and
                response[self._VALUE] == 'paused'):
            raise JemuConnectionException("Error: Couldn't resume jemu")
        self._logger.debug("Pause is waiting for stopped")

    def resume(self):
        if self.get_state() != 'paused':
            return

        self._logger.debug('resume')
        jemu_packet = self._jemu_connection.send_command(
            self._generate_json_command(self._START_COMMAND), self._name, self._peripheral_type
        )
        if not (self._DESCRIPTION in jemu_packet and jemu_packet[self._DESCRIPTION] == self._RESUMED):
            raise JemuConnectionException("Error: Couldn't resume jemu")

    def _wait_for_event_from_connection(self, event):
        while not event.is_set():
            if not self._jemu_connection.is_connected():
                raise JemuConnectionException("Error: The Emulator was closed unexpectedly.")
            event.wait(0.2)

    def cancel_stop(self):
        jemu_packet = self._jemu_connection.send_command(self._generate_json_command(self._CANCEL_STOP_ON_TICK),
                                                         self._name, self._peripheral_type)
        if not (self._DESCRIPTION in jemu_packet and jemu_packet[self._DESCRIPTION] == self._CANCEL_STOP_RESPONSE):
            raise JemuConnectionException("Error: Couldn't cancel stop")

    def _receive_packet(self, jemu_packet):
        if self._DESCRIPTION in jemu_packet:
            if jemu_packet[self._DESCRIPTION] == self._STOPPED:
                self._logger.debug('received stopped')
                self._stopped_packet_received.set()
            elif jemu_packet[self._DESCRIPTION] == self._TIMER_ID:
                cur_id = jemu_packet[self._VALUE]
                with self._timers_lock:
                    self._logger.debug('Calling timer id: {}'.format(cur_id))
                    self._timer_id_callback_dict[int(cur_id)]()
            elif jemu_packet[self._DESCRIPTION] == self._SUDO_EXIT:
                self._exit_code = int(jemu_packet[self._VALUE])
            elif jemu_packet[self._DESCRIPTION] == self._SP_MAX:
                if self._on_sp_max:
                    self._on_sp_max(int(jemu_packet[self._VALUE]))
            elif jemu_packet[self._DESCRIPTION] == self._CODE_COVERAGE:
                if self._on_code_coverage:
                    self._on_code_coverage(float(jemu_packet[self._VALUE]))

    def on_sp_max(self, callback):
        self._on_sp_max = callback

    def on_code_coverage(self, callback):
        self._on_code_coverage = callback

    def set_timer(self, ns, callback):
        with self._timers_lock:
            json_command = self._generate_json_command(self._COMMAND_SET_TIMER)
            json_command[self._NANO_SECONDS] = ns
            response = self._jemu_connection.send_command(json_command, self._name, self._peripheral_type)
            timer_id = response[self._TIMER_ID]
            self._logger.debug('Received id for timer: {}'.format(timer_id))
            self._timer_id_callback_dict.update({timer_id: callback})
            return response[self._TICKS]

    def get_state(self):
        self._logger.debug('Get state')
        jemu_packet = self._jemu_connection.send_command(self._generate_json_command(self._GET_STATE_COMMAND), self._name,
                                                         self._peripheral_type)
        self._logger.debug('Get state response:')
        self._logger.debug(jemu_packet)
        if jemu_packet is not None and \
                self._DESCRIPTION in jemu_packet and \
                jemu_packet[self._DESCRIPTION] == self._EMULATOR_STATE and \
                self._VALUE in jemu_packet:
            return jemu_packet[self._VALUE]
        else:
            raise JemuConnectionException("Error: Couldn't get jemu state")

    def get_device_time_ns(self):
        jemu_packet = self._jemu_connection.send_command(self._generate_json_command(self._GET_DEVICE_TIME), self._name,
                                                         self._peripheral_type)
        if jemu_packet is None:
            raise WrongStateError("Can't get device time when device is stopped")

        if self._DESCRIPTION in jemu_packet and \
                jemu_packet[self._DESCRIPTION] == self._DEVICE_TIME and \
                self._VALUE in jemu_packet:
            return jemu_packet[self._VALUE]
        else:
            raise JemuConnectionException("Error: Couldn't get device time")

    def get_exit_code(self):
        return self._exit_code

    def terminate(self):
        # print('terminate')
        self._jemu_connection.send_command_async(
            self._generate_json_command(self._TERMINATE), self._name, self._peripheral_type
        )

    def _get_pin_level_message(self, pin_num):
        return {
            self._COMMAND: self._GET_PIN_LEVEL,
            self._PIN_NUMBER: pin_num
        }

    def _set_pin_level_message(self, pin_num, pin_level):
        return {
            self._COMMAND: self._SET_PIN_LEVEL,
            self._PIN_LEVEL: pin_level,
            self._PIN_NUMBER: pin_num
        }

    def get_pin_level(self, pin_num):
        jemu_packet = self._jemu_connection.send_command(self._get_pin_level_message(pin_num), self._name, self._peripheral_type)
        if self._DESCRIPTION in jemu_packet and jemu_packet[self._DESCRIPTION] == self._VALUE_RESPONSE and self._VALUE in jemu_packet:
            return jemu_packet[self._VALUE]
        else:
            raise JemuConnectionException("Error: Couldn't get pin [{}] level".format(pin_num))

    def set_pin_level(self, pin_num, pin_level):
        self._jemu_connection.send_command_async(self._set_pin_level_message(pin_num, pin_level > 0), self._name, self._peripheral_type)
