import os
import re
import subprocess
import time
from time import sleep


from performance import DUMP_INTERVAL
from performance.Excel2 import Excel2
from performance.log import logd, tip


def parse_mem(mem_str=""):
    mem = {'total': 0}
    start = False
    for line in mem_str.splitlines():
        if line.strip() == "App Summary":
            start = True
            continue
        if not start:
            continue

        lines = re.split("\\s+", line.strip())
        if lines.__len__() < 2:
            continue
        if lines[0] == "TOTAL:":
            break
        value = lines[-1]
        lines.remove(value)
        key = " ".join(lines)
        mem[key] = int(value)
        mem['total'] += mem[key]
    return mem


class AndroidApp:

    def __init__(self, pkg, series=None):
        self.run = True
        self.series = series
        self.pkg = pkg
        self.output = ''
        self.file_prefix = 'ptk_' + pkg + '_' + time.strftime('%Y%m%d%H%M%S')

    def __str__(self):
        return self.pkg

    def check_pkg(self):
        is_ok = False
        pkgs = self.get_all_pkgs()
        assert isinstance(pkgs, str)
        for pkg in pkgs.splitlines():
            pkg = pkg.split(":")[1]
            if pkg == self.pkg:
                is_ok = True
                break
        if not is_ok:
            raise Exception('%s is not a valid package name.' % self.pkg)

    def get_all_pkgs(self):
        return self.adb_shell("pm list packages")

    def get_memory(self):
        return parse_mem(self.adb_shell("dumpsys meminfo " + self.pkg))

    def adb_shell(self, command="", _shell=True, check=True):
        args = ['adb']
        if self.series is not None and self.series != '':
            args.append('-s')
            args.append(self.series)
        args.append('shell')
        args.append(command)
        # return shell(args, command, _shell, check)
        r = ''
        try:
            r = subprocess.check_output(' '.join(args), shell=_shell, encoding='utf-8')
        except Exception as e:
            if check:
                raise e
            else:
                tip(e)
        return r

    def adb(self, command="", _shell=True, check=True):
        args = ['adb']
        if self.series is not None and self.series != '':
            args.append('-s')
            args.append(self.series)
        args.append(command)
        r = ''
        try:
            r = subprocess.check_output(' '.join(args), shell=_shell, encoding='utf-8')
        except Exception as e:
            if check:
                raise e
            else:
                tip(e)
        return r

    def monkey(self):
        tip("(%s) start monkey events..." % self.series)
        try:
            self.adb_shell("monkey -v -v -v -s 8888 --throttle 500 --ignore-crashes --ignore-timeouts "
                           "--ignore-security-exceptions --monitor-native-crashes  --hprof --pct-touch 8 "
                           "--pct-motion 10 --bugreport "
                           "--pct-appswitch 5 --pct-majornav 5 --pct-nav 0 --pct-syskeys 0 --pct-trackball 60 "
                           "-p %s %d > %s" % (self.pkg, 999999999, self.get_output_file(".monkey")))
        except Exception as e:
            tip("(%s) monkey stopped!!!" % self.series, e)

    def stop_monkey(self):
        self.run = False
        self.kill_process_name("com.android.com")

    def dump_memory(self):
        tip("(%s) start dump..." % self.series)
        excel = Excel2()
        try:
            datas = self.get_memory()
            excel.create_memory_sheet(self.get_output_file(".xlsx"), datas)

            while self.run:
                datas = self.get_memory()
                excel.add_data(datas)
                logd(self.series + ' add data: ' + datas.values().__str__())
                sleep(DUMP_INTERVAL)
        except Exception as e:
            raise e
        finally:
            tip("(%s) dump stopped!!!" % self.series)
            self.run = False
            excel.save()
            self.stop_monkey()

    def stop_logcat(self):
        self.kill_process_name("logcat")

    def logcat_clear(self):
        # args = ['adb']
        # if self.series is not None:
        #     args.append('-s')
        #     args.append(self.series)
        # args.append("logcat -c")
        # subprocess.check_output(' '.join(args), shell=True)
        self.adb_shell("logcat -c")

    def logcat(self):
        # args = ['adb']
        # if self.series is not None:
        #     args.append('-s')
        #     args.append(self.series)
        # args.append('logcat > %s' % self.get_output_file(".logcat"))
        #
        # process = subprocess.check_output(' '.join(args), shell=True)
        self.adb_shell("logcat -v threadtime > %s " % self.get_output_file(".logcat"))

    def logcat_e(self):
        # args = ['adb']
        # if self.series is not None:
        #     args.append('-s')
        #     args.append(self.series)
        # args.append('logcat *:E > %s' % self.get_output_file(".e.logcat"))
        #
        # subprocess.check_output(' '.join(args), shell=True)
        self.adb_shell("logcat -v threadtime *:E > %s " % self.get_output_file(".e.logcat"))

    def kill_process(self, pid):
        self.adb_shell("kill -9 %s" % pid)

    def kill_process_name(self, process_name):
        logd(self.series + " try stop process " + process_name)
        line_str = self.top_1()
        assert isinstance(line_str, str)
        lines = line_str.splitlines()
        for line in lines:
            els = re.split("\\s+", line.strip())
            if els.__len__() < 3:
                continue
            if not els[-1].startswith(process_name):
                continue
            pid = els[0]
            process = els[-1]
            try:
                tip("killing process %s(%s)..." % (process, pid))
                self.kill_process(pid)
            except Exception as e:
                tip("kill process %s(%s) failed!" % (process, pid), e)
                pass

    def get_output_file(self, suffix):
        assert isinstance(suffix, str)
        return self.output + os.path.sep + self.file_prefix + suffix

    def start(self):
        component = self.get_launcher_component2()
        if component is None:
            raise Exception("start app failed, cannot found app component, pkg: %s" % self.pkg)
        self.adb_shell("am start -n %s" % component)

    """ 
        获取AndroidManifest.xml中标记为Launcher的组件名称,
        cat= android.intent.category.LAUNCHER
        前提是app已经启动
    """

    def get_launcher_component(self):
        component = ''
        lines = self.adb_shell("dumpsys activity activities")
        assert isinstance(lines, str)
        for line in lines.splitlines():
            if line.__contains__("android.intent.category.LAUNCHER"):
                cmp_str = re.split("\\s+", line)[-1]
                component = cmp_str.split("=")[-1].replace("}", "")
                break
        return component

    """ 
        获取AndroidManifest.xml中标记为Launcher的组件名称,
        cat= android.intent.category.LAUNCHER
    """

    def get_launcher_component2(self):
        found_main = False
        lines = self.adb_shell("pm dump %s" % self.pkg).splitlines()
        component = None
        component_line = None
        for line in lines:
            assert isinstance(line, str)
            if line.strip() == 'android.intent.action.MAIN:':
                found_main = True
                continue
            if found_main:
                component_line = line
                break
        if component_line is None:
            return None
        component_line_splits = re.split("\\s+", component_line.strip())
        for split_word in component_line_splits:
            if split_word.startswith(self.pkg):
                component = split_word
                break
        return component

    """ 等待app启动 """

    def waiting_for_start(self):
        for i in range(10):
            process_start = False
            line_str = self.top_1()
            assert isinstance(line_str, str)
            lines = line_str.splitlines()
            for line in lines:
                words = re.split("\\s+", line.strip())
                if len(words) < 3:
                    continue
                if words[0].strip() == 'PID' or words[1] == 'PID':
                    process_start = True
                    continue
                if process_start:
                    pid = words[0]
                    name = words[-1].strip()
                    if name.startswith(self.pkg):
                        return pid
            sleep(1)
        return 0

    def top_1(self):
        return self.adb_shell("top -n 1")

    """ 清除历史日志 """
    def log_clear(self):
        dir = "/storage/self/primary"
        try:
            self.adb_shell("rm %s/app_crash*" % dir)
            self.adb_shell("rm %s/anr_*" % dir)
        except Exception as e:
            logd(e=e)

    def collect_logs(self, src_dir="/storage/self/primary"):
        # app_crash_dir = self.output + os.path.sep + "app_crash"
        # app_anr_dir = self.output + os.path.sep + "anr"
        # os.makedirs(app_crash_dir, exist_ok=True)
        # os.makedirs(app_anr_dir, exist_ok=True)

        ptk_crash_dir = src_dir + os.path.sep + "ptk_app_crash"
        self.adb_shell("mkdir -p %s" % ptk_crash_dir)
        self.adb_shell("mv %s/app_crash* %s" % (src_dir, ptk_crash_dir), check=False)
        self.adb("pull %s %s" % (ptk_crash_dir, self.output), check=False)
        self.adb_shell("rm -rf %s" % ptk_crash_dir)

        ptk_anr_dir = src_dir + os.path.sep + "ptk_anr"
        self.adb_shell("mkdir -p %s" % ptk_anr_dir)
        self.adb_shell("mv %s/anr_* %s" % (src_dir, ptk_anr_dir), check=False)
        self.adb("pull %s %s" % (ptk_anr_dir, self.output), check=False)
        self.adb_shell("rm -rf %s" % ptk_anr_dir)

    def ls(self, dir):
        return self.adb_shell("ls %s" % dir)


def shell(args, command='', _shell=True, check=False):
    with subprocess.Popen(" ".join(args), stdin=subprocess.PIPE,
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                          encoding="utf-8", shell=_shell) as process:
        try:
            stdout, stderr = process.communicate(command, timeout=3000)
        except subprocess.TimeoutExpired:
            stdout, stderr = process.communicate()
            raise subprocess.TimeoutExpired(process.args, 3000, output=stdout,
                                            stderr=stderr)
        except Exception as e:
            tip(e=e)
            raise
        retcode = process.poll()
        if check and retcode:
            raise Exception(stderr, retcode)
    return stdout


def monkey(app):
    assert isinstance(app, AndroidApp)
    app.monkey()


def stop(app):
    assert isinstance(app, AndroidApp)
    tip("(%s) try to stop monkey & logcat..." % app.series)
    app.run = False
    stop_monkey(app)
    stop_logcat(app)


def stop_monkey(app):
    assert isinstance(app, AndroidApp)
    for i in range(3):
        app.stop_monkey()
        sleep(0.5)


def stop_logcat(app):
    assert isinstance(app, AndroidApp)
    for i in range(3):
        app.stop_logcat()
        sleep(0.5)
