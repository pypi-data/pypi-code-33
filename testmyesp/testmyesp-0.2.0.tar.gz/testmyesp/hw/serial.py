
import serial


class SerialWithLog(serial.Serial):
    def __init__(self, port, baud):
        self._read_log = b''
        self._write_log = b''

        super().__init__(port, baud, timeout=0, write_timeout=0)

    def read(self, size=1):
        data = super().read(size)
        self._read_log += data

        return data

    def read_available(self):
        while self.is_open:
            available = self.in_waiting
            if not available:
                break

            self.read(available)

    def write(self, data):
        self._write_log += data

        return super().write(data)

    @property
    def read_log(self):
        return self._read_log

    @property
    def write_log(self):
        return self._write_log
