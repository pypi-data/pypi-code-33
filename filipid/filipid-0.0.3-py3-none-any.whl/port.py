import serial
import logging
import time
import serial.tools.list_ports


def log_data(logger, message, verbosity: bool=False):
    if verbosity:
        logger.info(message)


class Port:
    def __init__(self, port: str = None, baudrate: int = 19200, timeout: int = 1, verbosity: bool = False):
        """
        Initialize serial port
        :param port: string containing port name
        :param baudrate:
        :param timeout:
        :param verbosity:
        """
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
        self.verbosity = verbosity
        self.logger = None
        if verbosity:
            logging.basicConfig(level=logging.INFO)
            self.logger = logging.getLogger(__name__)
        log_data(self.logger, 'Port init started ', self.verbosity)
        self.ser = serial.Serial(
                port=port,
                baudrate=baudrate,
                timeout=timeout
        )
        log_data(self.logger, 'Port init completed ', self.verbosity)

    def send(self, data: list, sleep: float = 0.02) -> list:
        """
        Send data package to the designed port
        :param data: list of data points
        :param sleep: time to wait between write and read methods in seconds
        :return: list of integers
        """
        log_data(self.logger, 'Sending data started ', self.verbosity)
        proc_data = bytearray(data)
        self.ser.write(proc_data)
        time.sleep(sleep)
        rsp = self.ser.read_all()
        log_data(
            self.logger,
            f'Sending data completed, received {list(rsp)} ',
            self.verbosity
        )
        return list(rsp)

    def read(self):
        """
        Read all bytes currently available in the buffer of the OS.
        :return: list of integers
        """
        log_data(self.logger, 'Reading data started ', self.verbosity)
        rsp = self.ser.read_all()
        log_data(
            self.logger,
            f'Reading data completed, received {list(rsp)}',
            self.verbosity
        )
        return list(rsp)
