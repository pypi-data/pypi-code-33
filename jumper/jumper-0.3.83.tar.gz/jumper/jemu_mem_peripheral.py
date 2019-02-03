"""
:copyright: (c) 2017 by Jumper Labs Ltd.
:license: Apache 2.0, see LICENSE.txt for more details.
"""
from queue import Queue
from jemu_external_peripheral_base import ExternalPeripheralBase
from common import JemuConnectionException


class JemuMemPeripheral(ExternalPeripheralBase):
    _LEVEL_HIGH = 1
    _LEVEL_LOW = 0

    _VALUE = "value"
    _COMMAND = "command"
    _PERIPHERAL_NAME = "peripheral_name"
    _PERIPHERAL_TYPE = "peripheral_type"
    _REG_ADDRESS = "address"
    _COMMAND_SET_REG = "set_reg_value"
    _COMMAND_GET_REG = "get_reg_value"
    _DESCRIPTION = "description"
    _VALUE_RESPONSE = "value_response"

    def __init__(self, jemu_connection, name, peripheral_type, generators):
        ExternalPeripheralBase.__init__(self, jemu_connection, name, peripheral_type, generators)

    def _set_reg_json(self, register, value):
        return {
            self._REG_ADDRESS: register,
            self._VALUE: value,
            self._COMMAND: self._COMMAND_SET_REG,
        }

    def _get_reg_json(self, register):
        return {
            self._REG_ADDRESS: register,
            self._COMMAND: self._COMMAND_GET_REG,
        }

    def set_register_value(self, register, value):
        self.send_command(self._set_reg_json(register, value))

    def get_register_value(self, register):
        jemu_packet = self.send_command(self._get_reg_json(register))
        if self._DESCRIPTION in jemu_packet and jemu_packet[self._DESCRIPTION] == self._VALUE_RESPONSE and self._VALUE in jemu_packet:
            return jemu_packet[self._VALUE]
        else:
            raise JemuConnectionException("Error: Couldn't get register [{}] value".format(register))
