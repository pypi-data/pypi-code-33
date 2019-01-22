import os
import sys
import threading
from getopt import getopt

from performance.android import AndroidApp

from performance import VERSION, android
from performance import android_device
from performance.android_device import Device
from performance.log import tip


def usage():
    pass


def version():
    return '.'.join(str(v) for v in VERSION)


def main():
    #
    devices = None
    output = os.path.abspath(os.path.curdir)
    series = None
    stop = False

    hours = 10.0
    try:
        opts, args = getopt(sys.argv[1:], "d:o:t:shv")
        for op, value in opts:
            if op == '-o':
                output = value
            elif op == '-d':
                series = value
            elif op == '-h':
                usage()
                exit(0)
            elif op == '-v':
                print("pkt: " + version())
                exit(0)
            elif op == '-t':
                hours = float(value)
            elif op == '-s':
                stop = True
        pkg = args[0]
        if pkg is None:
            raise Exception("package name should not be none.")

        devices = android_device.get_devices()

        if not len(devices):
            tip("error: no devices connected !!")
            return
        for device in devices:
            if output is not None:
                device.output = output
            if series is not None and device.series == series:
                devices = [device]
                break

        tip("检测应用: " + pkg)
        tip("检测时长: %s(s)" % str(int(hours * 60 * 60)))
        tip("输出目录: " + output)
        tip("检测设备: " + str(devices))
        tip("")

        if stop:
            for device in devices:
                device.pkg = pkg
                device.app = AndroidApp(pkg, series=device.series)
                device.stop()
                return

        device_threads = []
        for device in devices:
            assert isinstance(device, Device)
            device.pkg = pkg
            device_thread = DeviceThread(device)
            device_thread.start()
            device_threads.append(device_thread)

        for thread in device_threads:
            time_out = hours * 60 * 60
            thread.join(timeout=time_out)

    except Exception as e:
        raise e
    finally:
        if devices is None:
            return
        for device in devices:
            device.app.run = False


class DeviceThread(threading.Thread):

    def __init__(self, device):
        super().__init__()
        assert isinstance(device, Device)
        self.device = device
        self.setDaemon(False)

    def run(self):
        try:
            self.device.start()
        except Exception as e:
            print(e)
        finally:
            android.stop(self.device.app)
