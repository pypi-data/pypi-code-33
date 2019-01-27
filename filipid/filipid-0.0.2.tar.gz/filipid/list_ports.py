import serial.tools.list_ports


def main():
    available_devices = [
                i.device for i in list(serial.tools.list_ports.comports())
            ]
    print('\n'.join(available_devices))

