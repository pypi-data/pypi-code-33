from threading import Lock
from .timeout_dec import timeout
import threading


class JemuI2cMaster(object):

    _ACK = "ack"
    _ADDRESS = "address"
    _COMMAND = "command"
    _DATA = "data"
    _DESCRIPTION = "description"
    _EVENT_TYPE = "event_type"
    _EVENT_WRITE_FINISHED = "master_write_finished"
    _EVENT_READ_FINISHED = "master_read_finished"
    _EXTERNAL_PERIPHERAL = "External"
    _FREQUENCY = "i2c_frequency"
    _I2C_EVENT = "i2c_event"
    _NUM_BYTES_TO_READ = "num_bytes_to_read"
    _READ = "master_read"
    _SET_FREQUENCY = "master_set_frequency"
    _WRITE = "master_write"
    _WRITE_READ = "master_write_read"

    def __init__(self, jemu_connection, name):
        self._name = name
        self._jemu_connection = jemu_connection
        self._jemu_connection.register(self.receive_packet)
        self._device_address = None
        self._device_address_mask = None
        self._lock = Lock()
        self._data_read = None
        self._read_finished = threading.Event()
        self._write_finished = threading.Event()

    def write(self, address, data):
        """
        Mater write data to slave
        :param address: slave device address
        :param data: data to send (bytes)
        """
        self._jemu_connection.send_command(
            self._master_write_json(address, data),
            self._name,
            self._EXTERNAL_PERIPHERAL)
        self._wait_for_write_finished()

    def read(self, address, num_bytes_to_read):
        """
        Mater read data from slave
        :param address: slave device address
        :param num_bytes_to_read: number of bytes to read
        :return data read
        """
        self._jemu_connection.send_command(
            self._master_read_json(address, num_bytes_to_read),
            self._name,
            self._EXTERNAL_PERIPHERAL)
        self._wait_for_read_finished()
        return self._convert_data_from_hex_string(self._data_read)

    def write_read(self, address, data, num_bytes_to_read):
        """
        Mater write data to slave
        :param address: slave device address
        :param data: data to send (bytes)
        :param num_bytes_to_read: number of bytes to read
        """
        self._jemu_connection.send_command(
            self._master_write_read_json(address, data, num_bytes_to_read),
            self._name,
            self._EXTERNAL_PERIPHERAL)
        self._wait_for_read_finished()
        return self._convert_data_from_hex_string(self._data_read)

    def set_frequency(self, i2c_frequency):
        """
        Set I2C frequency
        :param i2c_frequency
        """
        self._jemu_connection.send_command(
            self._master_set_frequency_json(i2c_frequency),
            self._name,
            self._EXTERNAL_PERIPHERAL)

    @staticmethod
    def _convert_data_to_hex_string(data):
        return data.encode('hex')

    @staticmethod
    def _convert_data_from_hex_string(data):
        return data.decode('hex')

    def _master_write_json(self, address, data):
        data = self._convert_data_to_hex_string(data)
        return {
            self._COMMAND: self._WRITE,
            self._ADDRESS: address,
            self._DATA: data,
        }

    def _master_read_json(self, address, num_bytes_to_read):
        return {
            self._COMMAND: self._READ,
            self._ADDRESS: address,
            self._NUM_BYTES_TO_READ: num_bytes_to_read,
        }

    def _master_write_read_json(self, address, data, num_bytes_to_read):
        data = self._convert_data_to_hex_string(data)
        return {
            self._COMMAND: self._WRITE_READ,
            self._ADDRESS: address,
            self._DATA: data,
            self._NUM_BYTES_TO_READ: num_bytes_to_read,
        }

    def _master_set_frequency_json(self, i2c_frequency):
        return {
            self._COMMAND: self._SET_FREQUENCY,
            self._FREQUENCY: i2c_frequency
        }

    def _handle_write_finished(self):
        self._jemu_connection.send_response(self._read_response_json(True), self._name, self._EXTERNAL_PERIPHERAL)
        self._write_finished.set()

    def _handle_read_finished(self, jemu_packet):
        self._data_read = jemu_packet[self._DATA]
        self._jemu_connection.send_response(self._read_response_json(True), self._name, self._EXTERNAL_PERIPHERAL)
        self._read_finished.set()

    def _read_response_json(self, ack):
        return {
            self._ACK: ack,
        }

    @timeout(5)
    def _wait_for_write_finished(self):
        while not self._write_finished.wait(timeout=0.2):
            pass
        self._write_finished.clear()

    @timeout(5)
    def _wait_for_read_finished(self):
        while not self._read_finished.wait(timeout=0.2):
            pass
        self._read_finished.clear()

    def receive_packet(self, jemu_packet):
        # print (jemu_packet)
        with self._lock:
            if self._DESCRIPTION in jemu_packet and jemu_packet[self._DESCRIPTION] == self._I2C_EVENT \
                  and self._EVENT_TYPE in jemu_packet:
                if jemu_packet[self._EVENT_TYPE] == self._EVENT_READ_FINISHED:
                    self._handle_read_finished(jemu_packet)
                elif jemu_packet[self._EVENT_TYPE] == self._EVENT_WRITE_FINISHED:
                    self._handle_write_finished()
