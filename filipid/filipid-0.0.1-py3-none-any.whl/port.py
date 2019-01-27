import serial
import logging
import time
import serial.tools.list_ports


class Port:
    def __init__(self, port: str = None, baudrate: int = 19200, timeout: int = 1, verbosity: bool = False):
        if not port:
            # Raise exception if port is not defined
            raise Exception(
                f'Port should be defined!'
            )
        available_devices = [
            i.device for i in list(serial.tools.list_ports.comports())
        ]
        if port not in available_devices:
            raise Exception(
                f'Requested port /{port}/ is not available'
            )
        if verbosity:
            logging.basicConfig(level=logging.INFO)
            self.logger = logging.getLogger(__name__)

        self.ser = serial.Serial(
                port=port,
                baudrate=baudrate,
                timeout=timeout
        )
        self.verbosity = verbosity

    def send(self, data: list, sleep: float = 0.02) -> list:
        """
        Send data package to the designed port
        :param data: list of data points
        :param sleep: time to wait between write and read methods in seconds
        :return: list of integers
        """
        proc_data = bytearray(data)
        self.ser.write(proc_data)
        time.sleep(sleep)
        rsp = self.ser.read_all()
        return list(rsp)

    def read(self):
        """
        Read all bytes currently available in the buffer of the OS.
        :return: list of integers
        """
        rsp = self.ser.read_all()
        return list(rsp)


if __name__ == '__main__':
    port = Port(port='/dev/cu.usbserial-A901A1JZ')
    tmp = port.send([253, 252, 2, 3, 0], 0.04)
    print(tmp)
    tmp = port.send([253, 251, 2, 0], 0.02)
    print(tmp)
    tmp = port.send([255, 2], 0.02)
    print(tmp)