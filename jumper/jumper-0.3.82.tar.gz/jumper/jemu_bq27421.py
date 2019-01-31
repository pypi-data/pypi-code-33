"""
:copyright: (c) 2017 by Jumper Labs Ltd.
:license: Apache 2.0, see LICENSE.txt for more details.
"""
from jemu_mem_peripheral import JemuMemPeripheral


class JemuBQ27421(JemuMemPeripheral):
    _INTERRUPT = "interrupts"
    _COMMAND_SET_INTERRUPT = "set_interrupt"
    _COMMAND = "command"

    def __init__(self, jemu_connection, name, peripheral_type, generators):
        JemuMemPeripheral.__init__(self, jemu_connection, name, peripheral_type, generators)

    def _battery_interrupt_json(self):
        return {
            self._COMMAND: self._COMMAND_SET_INTERRUPT,
        }

    def interrupt(self):
        """
        This function activates an interrupt in the bq27421 peripheral.
        On interrupt a 1 ms pulse is sent out over gpout pin.
        """
        self._jemu_connection.send_command_async(self._battery_interrupt_json(), self._name, self._peripheral_type)
