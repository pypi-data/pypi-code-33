"""
:copyright: (c) 2017 by Jumper Labs Ltd.
:license: Apache 2.0, see LICENSE.txt for more details.
"""
from threading import Lock
from time import sleep
from common import TimeoutException
from common import WrongStateError
import sys


class JemuUartJson(object):
    _DESCRIPTION = "description"
    _VALUE_RESPONSE = "value_response"
    _COMMAND = "command"
    _WRITE_DATA = "write_uart_data"
    _READ_DATA = "read_uart_data"
    _UART_EVENT = "uart_event"
    _NAME = "name"
    _VALUE = "value"
    _LINE_SEPARATOR = b'\r\n'
    _LINE_SEPARATOR2 = b'\n'

    def __init__(self, vlab, uart_name, mcu_name="nrf52832"):
        self._uart_callback = None
        self._jemu_socket_manager = None
        self._peripheral_type = mcu_name
        self._uart_buffer = None
        self._vlab = vlab
        self._lock = Lock()
        self._print_to_screen = False
        self._callback_read_uart_line = None
        self._callback_read_data = None
        self._lock_callback = Lock()
        self._lock_read_data_callback = Lock()
        self._uart_name = uart_name
        self.esc = False

    def print_uart_to_screen(self):
        self._print_to_screen = True

    def open(self):
        self._uart_buffer = b''
        # TODO: jemu_connection should be a member instead of using a private member from another class
        if self._vlab._jemu_connection:
            self._vlab._jemu_connection.register(self.receive_packet)

    def receive_packet(self, jemu_packet):
        if self._DESCRIPTION in jemu_packet and jemu_packet[self._DESCRIPTION] == self._UART_EVENT and self._VALUE in jemu_packet:

            # This packet is not for this uart
            if jemu_packet[self._NAME] != self._uart_name:
                return  

            with self._lock:
                new_data = chr(jemu_packet[self._VALUE])
                if self._print_to_screen:
                    # dansheme 18/4/2018: Flush is needed for testing purposes.
                    # BLE test is setting stdout of this process to PIPE and data is not being flushed automatically
                    # by the kernel.
                    sys.stdout.write(new_data)
                    sys.stdout.flush()
                self._uart_buffer += new_data

            self._inform_uart_callback_if_needed(jemu_packet[self._VALUE])

    def _inform_uart_callback_if_needed(self, unichar):
        with self._lock_read_data_callback:
            if self._callback_read_data:
                self._callback_read_data(unichar)

        # send data of uart without esc+E (that is \n)
        end_of_line_detected = False
        buffer_to_send = ""
        if unichar == 27:
            # found esc in buffer
            self.esc = True
            return
        elif unichar == 69 and self.esc:
            # found esc+E (27 and 69) it's like new line in buffer
            buffer_to_send = self._uart_buffer[:-2]
            end_of_line_detected = True
        elif self._LINE_SEPARATOR in self._uart_buffer or self._LINE_SEPARATOR2 in self._uart_buffer:
            # found line separator in buffer
            buffer_to_send = self._uart_buffer
            end_of_line_detected = True

        if end_of_line_detected:
            with self._lock_callback:
                if self._callback_read_uart_line:
                    self._empty_buffer()
                    self._callback_read_uart_line(buffer_to_send)

        self.esc = False

    def _write_to_uart_message(self, data):
        return {
            self._COMMAND: self._WRITE_DATA,
            self._VALUE: data
        }

    def write(self, data):
        """
         Writes data to UART

         :param data: Data to write
         """
        chars = [ord(c) for c in data]
        for c in chars:
            self.write_char(c)

    def write_char(self, char):
        """
         Writes char to UART

         :param char: char to write (ASCII value)
         """
        if self._vlab._jemu_connection:
            json_pack = self._write_to_uart_message(char)
            peripheral_name = self._uart_name
            peripheral_type = self._peripheral_type
            self._vlab._jemu_connection.send_command_async(json_pack, peripheral_name, peripheral_type)

    def read(self):
        """
        :return: data available on the UART device. Returns an empty bytes string if no data is available.
        """
        with self._lock:
            data = self._uart_buffer
            self._uart_buffer = b''
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
        if timeout == 0:
            raise TimeoutException("timeout while waiting for data from uart")

        original_state = self._vlab.get_state()

        if original_state == 'running':
            self._vlab.pause()
        elif original_state != 'paused':
            raise WrongStateError('state should be paused or running but was {}'.format(original_state))

        if timeout is not None:
            self._vlab.stop_after_ms(timeout)

        self._vlab.resume()

        while data not in self._uart_buffer and self._vlab.get_state() == 'running':
            sleep(0.2)

        if timeout is not None:
            self._vlab.cancel_stop()

        if original_state == 'running':
            self._vlab.resume()
        elif original_state == 'paused':
            self._vlab.pause()

        with self._lock:
            if data in self._uart_buffer:
                tmp = self._uart_buffer
                self._uart_buffer = b''
                return tmp

        raise TimeoutException("timeout while waiting for data from uart")

    def read_line(self, line_separator=_LINE_SEPARATOR):
        while line_separator not in self._uart_buffer:
            sleep(0.2)
        return self._get_data_line(line_separator)

    def on_uart_read_line(self, callback):
        with self._lock_callback:
            self._callback_read_uart_line = callback

    def on_uart_data(self, callback):
        with self._lock_read_data_callback:
            self._callback_read_data = callback

    def _empty_buffer(self):
        with self._lock:
            self._uart_buffer = b''

    def _get_data_line(self, line_separator=_LINE_SEPARATOR):
        with self._lock:
            line_length = self._uart_buffer.find(line_separator) + len(line_separator)
            data = self._uart_buffer[:line_length]
            self._uart_buffer = self._uart_buffer[line_length:]
        return data
