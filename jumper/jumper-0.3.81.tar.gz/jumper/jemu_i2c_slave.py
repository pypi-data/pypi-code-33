from threading import Lock


class JemuI2cSlave(object):
    _DEVICE_ADDRESS = "device_address"
    _EVENT_TYPE = "event_type"
    _DEVICE_ADDRESS_MASK = "mask"

    _EVENT_TYPE_READ = "on_read"
    _ADDRESS = "address"
    _READ_INDEX = "read_index"

    _EVENT_TYPE_WRITE = "on_write"
    _WRITE_INDEX = "write_index"
    _DATA = "data"
    _ACK = "ack"
    _RESPONSE = "response"

    _EVENT_TYPE_START = "on_start"
    _EVENT_TYPE_STOP_READ = "on_stop_read"
    _EVENT_TYPE_STOP_WRITE = "on_stop_write"
    _DESCRIPTION = "description"
    _I2C_EVENT = "i2c_event"
    _DEVICE_TIME = "device_time"

    _COMMAND = "command"
    _COMMAND_SET_DEVICE_ADDRESS = "set_device_address"
    _EXTERNAL_PERIPHERAL = "External"

    def __init__(self, jemu_connection, name):
        self._name = name
        self._jemu_connection = jemu_connection
        self._jemu_connection.register(self.receive_packet)
        self._lock = Lock()
        self._device_address = None
        self._device_address_mask = None
        self._on_read_callback = None
        self._on_write_callback = None
        self._on_start_callback = None
        self._on_stop_read_callback = None
        self._on_stop_write_callback = None

    def on_master_read(self, callback):
        """
        Registers a callback to be called when the master is trying to read 1 byte from the slave.

        :param callback: A callback function that will be called with the following arguments (device_address, read_index). The callback must return a tuple: (ack, response_byte).
        """
        with self._lock:
            self._on_read_callback = callback

    def on_master_write(self, callback):
        """
        Registers a callback to be called when the master is trying to write a byte to the slave.

        :param callback: A callback function that will be called with the following arguments (device_address, write_index, data_byte). The callback must return the ack as True/False.
        """
        with self._lock:
            self._on_write_callback = callback

    def on_master_stop_read(self, callback):
        """
        Registers a callback to be called when the master is sending a stop signal after a read sequence.

        :param callback:
        """
        with self._lock:
            self._on_stop_read_callback = callback

    def on_master_stop_write(self, callback):
        """
        Registers a callback to be called when the master is sending a stop signal.

        :param callback:
        """
        with self._lock:
            self._on_stop_write_callback = callback

    def _master_read_response_json(self, ack, response):
        return {
            self._ACK: ack,
            self._RESPONSE: response,
        }

    def _master_write_response_json(self, ack):
        return {
            self._ACK: ack,
        }

    def _address_json(self):
        json_set_address = {
            self._DEVICE_ADDRESS: self._device_address,
            self._COMMAND: self._COMMAND_SET_DEVICE_ADDRESS,
        }
        if self._device_address_mask:
            json_set_address[self._DEVICE_ADDRESS_MASK] = self._device_address_mask

        return json_set_address

    def _send_master_read_response(self, ack, response):
        self._jemu_connection.send_response(self._master_read_response_json(ack, response), self._name,
                                            self._EXTERNAL_PERIPHERAL)

    def _send_master_write_response(self, ack):
        self._jemu_connection.send_response(self._master_write_response_json(ack), self._name,
                                            self._EXTERNAL_PERIPHERAL)

    def set_address(self, address, mask=None):
        """
        Sets the address of the device on the I2C bus

        """
        with self._lock:
            self._device_address = address
            if mask:
                self._device_address_mask = mask
        self._jemu_connection.send_command(self._address_json(), self._name, self._EXTERNAL_PERIPHERAL)

    def _handle_master_read(self, jemu_packet):
        address = jemu_packet[self._ADDRESS]
        read_index = jemu_packet[self._READ_INDEX]
        if self._on_read_callback:
            ack, response = self._on_read_callback(address, read_index)
            if not ack or not response:
                raise Exception("on_master_read callback must return a tuple: (ack as True/False, response_byte)")
            if type(response) != int:
                response = int(response.encode('hex'), 16)
            self._send_master_read_response(ack, response)
        else:
            self._send_master_read_response(False, {})

    def _handle_master_write(self, jemu_packet):
        if self._on_write_callback:
            ack = self._on_write_callback(
                jemu_packet[self._ADDRESS],
                jemu_packet[self._WRITE_INDEX],
                jemu_packet[self._DATA])
            if ack is None:
                raise Exception("on_master_write callback must return the ack as True/False")
            self._send_master_write_response(ack)
        else:
            self._send_master_write_response(False)

    def _is_device_address(self, device_address, address):
        if self._device_address_mask:
            return (device_address & self._device_address_mask) == (address & self._device_address_mask)
        else:
            return device_address == address

    def receive_packet(self, jemu_packet):
        # print (jemu_packet)
        with self._lock:
            if self._DESCRIPTION in jemu_packet and jemu_packet[self._DESCRIPTION] == self._I2C_EVENT \
                  and self._DEVICE_ADDRESS in jemu_packet \
                  and self._is_device_address(self._device_address, jemu_packet[self._DEVICE_ADDRESS]) \
                  and self._EVENT_TYPE in jemu_packet:
                if jemu_packet[self._EVENT_TYPE] == self._EVENT_TYPE_READ:
                    self._handle_master_read(jemu_packet)
                elif jemu_packet[self._EVENT_TYPE] == self._EVENT_TYPE_WRITE:
                    self._handle_master_write(jemu_packet)
                elif jemu_packet[self._EVENT_TYPE] == self._EVENT_TYPE_STOP_READ:
                    if self._on_stop_read_callback:
                        self._on_stop_read_callback()
                elif jemu_packet[self._EVENT_TYPE] == self._EVENT_TYPE_STOP_WRITE:
                    if self._on_stop_write_callback:
                        self._on_stop_write_callback()
