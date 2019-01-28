import time
import pywinusb.hid as hid


class _TemperWindows:
    def __init__(self):
        self.read_data = None
        self.read_data_received = False

    def raw_data_handler(self, data):
        self.read_data = data
        self.read_data_received = True

    @staticmethod
    def convert_data_to_temperature(data):
        return float(data[3] * 256 + data[4]) / 100

    def get_temperature(self, thermometer_index=0):
        self.read_data = None
        self.read_data_received = False

        devices = hid.HidDeviceFilter(vendor_id=0x413d, product_id=0x2107).get_devices()

        if thermometer_index > len(devices) - 1:
            return None

        device = devices[thermometer_index]

        try:
            device.open()
            device.set_raw_data_handler(self.raw_data_handler)

            write_data = [0x00, 0x01, 0x80, 0x33, 0x01, 0x00, 0x00, 0x00, 0x00]

            # reset read_data_received before sending our data
            self.read_data_received = False

            device.send_output_report(write_data)

            # wait for read data to be received
            sleep_amount = 0.01  # 0.01 to start with to avoid an unnecessary long wait for the majority of time
            while self.read_data_received is False:
                time.sleep(sleep_amount)
                sleep_amount = 0.05  # 0.05 after to avoid causing high cpu

            # noinspection PyTypeChecker
            return self.convert_data_to_temperature(self.read_data)
        finally:
            device.close()


_temper_windows = None


# api is cleaner if the class isn't exposed
def get_temperature(thermometer_index=0):
    """Gets the temperature from a Temper USB thermometer.

    :param thermometer_index: If you have more than one thermometer, you can pick which one you want to check
    :return: The temperature in celsius or None if temperature couldn't be retrieved.
    """

    global _temper_windows  # avoiding instantiating the class each time the function is called

    # starts off None to avoid using any extra memory if the function doesn't end up being called
    if _temper_windows is None:
        _temper_windows = _TemperWindows()

    return _temper_windows.get_temperature(thermometer_index)


def _main():
    temperature = get_temperature()
    print(temperature)


if __name__ == '__main__':
    _main()
