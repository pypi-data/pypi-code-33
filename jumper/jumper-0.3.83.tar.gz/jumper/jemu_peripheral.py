"""
:copyright: (c) 2017 by Jumper Labs Ltd.
:license: Apache 2.0, see LICENSE.txt for more details.
"""
from common import JemuConnectionException

class FieldDescriptor:
    _RESPONSE_TIMEOUT = 10

    _VALUE = "value"
    _PERIPHERAL_NAME = "peripheral_name"
    _PERIPHERAL_TYPE = "peripheral_type"
    _FIELD_NAME = "field_name"
    _COMMAND = "command"
    _COMMAND_SET_VALUE = "set_value"
    _COMMAND_GET_VALUE = "get_value"
    _DESCRIPTION = "description"
    _GET_VALUE_RESPONSE = "get_value_response"

    def __init__(self, jemu_connection, name, field_name, peripheral_type):
        self._name = name
        self._jemu_connection = jemu_connection
        self._field_name = field_name
        self._peripheral_type = peripheral_type

    def set(self, val):
        self._jemu_connection.send_command_async(self._set_value_json(val), self._name, self._peripheral_type)

    def get(self):
        jemu_packet = self._jemu_connection.send_command(self._get_value_json(), self._name, self._peripheral_type)
        if self._DESCRIPTION in jemu_packet and jemu_packet[self._DESCRIPTION] == self._GET_VALUE_RESPONSE and self._VALUE in jemu_packet:
            return jemu_packet[self._VALUE]
        else:
            raise JemuConnectionException("Error: Couldn't get value from jemu peripheral")

    def _set_value_json(self, value):
        return {
            self._FIELD_NAME: self._field_name,
            self._VALUE: value,
            self._COMMAND: self._COMMAND_SET_VALUE
        }

    def _get_value_json(self):
        return {
            self._FIELD_NAME: self._field_name,
            self._COMMAND: self._COMMAND_GET_VALUE
        }


class JemuPeripheral:
    def __init__(self, jemu_connection, name, peripheral_type, generators):
        self._peripheral_type = peripheral_type
        self._name = name
        self._jemu_connection = jemu_connection

        if generators is not None:
            for field in generators:
                descriptor = FieldDescriptor(jemu_connection, name, field, peripheral_type)
                setattr(self, field, descriptor)
