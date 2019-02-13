import os
import re
import threading
import time

from performance import android, TODAY
from performance.android import AndroidApp
from performance.log import tip


class Device(object):
    def __init__(self):
        self.series = None
        self.state = None
        self.app = None
        self.output = os.path.curdir
        self.pkg = None
        self.duration = 0

    def __str__(self):
        return self.series

    def __repr__(self):
        return self.series

    def start(self, pkg=None):
        if self.series is None or self.series == '':
            raise Exception("empty device")
        if self.state == "offline":
            raise Exception("offline device: " + self.series)

        if pkg is None:
            pkg = self.pkg

        if pkg is None or pkg == '':
            raise Exception("未指定包名.")
        assert isinstance(pkg, str)

        self.app = AndroidApp(pkg, self.series)
        self.app.duration = self.duration

        # 检查app是否已经安装
        self.app.check_pkg()

        self.output = self.output + os.path.sep + TODAY + os.path.sep + self.pkg + os.path.sep + self.series
        if not os.path.isdir(self.output):
            os.makedirs(self.output)

        self.app.output = self.output
        self.app.ptk_anr_dir = self.output + os.path.sep + "ptk_anr"
        self.app.ptk_crash_dir = self.output + os.path.sep + "ptk_app_crash"

        # 清除sd卡目录下的历史crash，anr日志
        self.app.log_clear()

        try:
            monkey_thread = MonkeyThread(self.app)
            monkey_thread.setDaemon(True)
            monkey_thread.start()

            # 先清除logcat缓存
            self.app.logcat_clear()

            # 等待app启动
            tip("(%s) waiting for app start..." % self.series)
            pid = self.app.waiting_for_start()
            if pid:
                tip("(%s) app start success..." % self.series)
            else:
                tip("(%s) app start failed..." % self.series)
                raise Exception("app start failed!!!")

            logcat_thread = LogcatThread(self.app)
            logcat_thread.setDaemon(True)
            logcat_thread.start()

            logcat_e_thread = LogcatErrorThread(self.app)
            logcat_e_thread.setDaemon(True)
            logcat_e_thread.start()

            self.app.dump_memory()
        except Exception as e:
            raise e
        finally:
            self.app.stop_logcat()
            tip("(%s) process finished!!" % self.series)

    def stop(self, app=None):
        if app is None:
            app = AndroidApp(self.pkg, self.series)
        android.stop(app)


class MonkeyThread(threading.Thread):

    def __init__(self, app):
        threading.Thread.__init__(self)
        assert isinstance(app, AndroidApp)
        self.app = app

    def run(self):
        self.app.monkey()


class LogcatThread(threading.Thread):

    def __init__(self, app):
        threading.Thread.__init__(self)
        assert isinstance(app, AndroidApp)
        self.app = app

    def run(self):
        self.app.logcat()


class LogcatErrorThread(threading.Thread):

    def __init__(self, app):
        threading.Thread.__init__(self)
        assert isinstance(app, AndroidApp)
        self.app = app

    def run(self):
        self.app.logcat_e()


def get_devices():
    devices = []
    line_str = android.shell(['adb', 'devices'])
    assert isinstance(line_str, str)
    if line_str is None:
        return None
    lines = line_str.splitlines()
    for line in lines:
        device_arr = re.split("\\s+", line)
        if len(device_arr) != 2:
            continue
        device = Device()
        device.series = device_arr[0]
        device.state = device_arr[1]
        devices.append(device)
    return devices

