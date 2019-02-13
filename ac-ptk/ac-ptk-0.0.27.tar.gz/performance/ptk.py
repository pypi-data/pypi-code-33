import os
import sys
import threading
from getopt import getopt

import performance

from performance.android import AndroidApp

from performance import VERSION, android, properties, config
from performance import android_device
from performance.android_device import Device
from performance.config import WORK_DIR
from performance.log import tip


def usage():
    print("Performance Test Kit")
    print("usage: ptk [-d device] [-o output] [-t duration] [-p property_file] [-s] [-v] [-h] <app_package_name>")
    print()
    print("-h 打印此帮助")
    print("-d 设备号，可以通过adb devices命令拿到")
    print("-v 打印ptk版本号")
    print("-o 数据，日志的输出目录")
    print("-s 停止, 后面需要跟app包名")
    print("-t 时间(h), 可以是整数或者小数作为参数, 比如0.1,0.5,1,2,5,8..., 默认值是10")
    print("-p 属性文件,默认取 ~/ptk/ptk.properties")


def version():
    return '.'.join(str(v) for v in VERSION)


def main():
    #
    devices = None
    output = WORK_DIR
    series = None
    stop = False

    hours = 10.0
    try:
        opts, args = getopt(sys.argv[1:], "d:o:t:p:shv")
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
            elif op == '-p':
                if not os.path.exists(value):
                    tip("配置文件不存在: %s " % value)
                    exit(1)
                config.ptk_properties = properties.parse(value)
        if len(args) < 1:
            usage()
            exit(1)
        pkg = args[0]
        if pkg is None or pkg == '':
            usage()
            exit(0)

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

        if stop:
            for device in devices:
                device.pkg = pkg
                device.app = AndroidApp(pkg, series=device.series)
                device.stop()
                return

        tip("检测应用: " + pkg)
        tip("检查开始: " + performance.TIME)
        tip("检测时长: %s(s)" % str(int(hours * 60 * 60)))
        tip("输出目录: " + output)
        tip("检测设备: " + str(devices))
        tip("属性配置: " + str(os.path.abspath(config.ptk_properties.file_name)))
        tip("")

        device_threads = []
        for device in devices:
            assert isinstance(device, Device)
            device.pkg = pkg
            device.duration = hours
            device_thread = DeviceThread(device)
            device_thread.start()
            device_threads.append(device_thread)

        for thread in device_threads:
            time_out = hours * 60 * 60
            thread.join(timeout=time_out)

    except Exception as e:
        if devices is None:
            return
        for device in devices:
            device.app.success = False
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
            raise e
        finally:
            android.stop(self.device.app)
