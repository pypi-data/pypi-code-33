# -*- coding: utf-8 -*-
"""
Created on Wed Oct 11 08:18:59 2017

This script is designed to wrap around external services
and provide access to starting/stopping that service
using remote procedure calls.

@author: kjetil
"""
from __future__ import print_function


from SimpleXMLRPCServer import SimpleXMLRPCServer
import subprocess
import threading
import argparse
import select
import os
import sys
import logging
import logging.handlers
import signal
import time

if not (sys.platform == "linux" or sys.platform == "linux2"):
    print("Servicecontrol has been made for linux, whereas your system reports something else ({}). It probably wont work.\n\n".format(sys.platform))


# Import libc if possible so we can use PDEATHSIG
try:
    from ctypes import cdll
    libc = cdll['libc.so.6']
except Exception as e:
    libc = None

PR_SET_PDEATHSIG = 1

# Killer to catch sigterm and exit
class Killer:
    kill_now = False

    @classmethod
    def exit_gracefully(cls,signum, frame):
        cls.kill_now = True

    @classmethod
    def register_signal(cls, signum):
        signal.signal(signum, cls.exit_gracefully)


class LogFormatter(logging.Formatter):
    converter = time.gmtime
    DEFAULT_FORMAT =  'scontr - %(asctime)s - %(levelname)5s - "%(message)s"'

    def formatTime(self, record, datefmt=None):
        ct = self.converter(record.created)
        t = time.strftime("%Y-%m-%dT%H:%M:%S", ct)
        s = "%s.%03dZ" % (t, record.msecs)

        return s



log = logging.getLogger('servicecontrol')
log.setLevel(logging.DEBUG)

ch = logging.StreamHandler(sys.stdout)
formatter = LogFormatter(LogFormatter.DEFAULT_FORMAT)#'%(asctime)s - %(levelname)5s - "%(message)s"')
ch.setFormatter(formatter)
log.addHandler(ch)

log_output = logging.getLogger('servicecontrol-output')
log_output.setLevel(logging.DEBUG)
ch_output = logging.StreamHandler(sys.stdout)




class ServiceControl():

    # Maximum number of lines of stdout/stderr to keep in memory
    # to be returned on request over RPC
    MAX_BUFLEN = 50

    #
    # Number of seconds to allow for boot errors before initiating auto-restart sequences
    #
    MIN_BOOT_TIME = 3.0

    #
    # If autorestart is on and it dies within MIN_BOOT_TIME, delay for this amount of time before trying another restart
    #
    MIN_RESTART_TIME = 30

    #
    # The timeout after sending SIGTERM before trying again with SIGKILL (can be changed in constructor)
    #
    DEFAULT_KILL_TIMEOUT = 60

    #
    # The port numbe
    #
    DEFAULT_PORT_NO = 9000

    def __init__(self, args, addr="localhost", port=DEFAULT_PORT_NO, echo=True, autorestart=False, cputhreshold = None, kill_timeout=DEFAULT_KILL_TIMEOUT):
        self.args = args
        self._p = None
        self._addr = addr
        self._port = port
        self._stdout = []
        self._stderr = []
        self.cpu_threshold = cputhreshold
        self._echo = echo
        self._stop_monitor = False
        self.autorestart = autorestart
        self._kill_timeout = kill_timeout

        self.server = SimpleXMLRPCServer((self._addr, self._port), allow_none=True)
        self._pthr_rpc = threading.Thread(target=self.server.serve_forever)
        self._pthr_rpc.daemon = True
        self._pthr_rpc.start()

        # Make RPC calls more usable by publishing functions
        self.server.register_introspection_functions()

        # Register the functions
        self.server.register_function(self.start)
        self.server.register_function(self.kill)
        self.server.register_function(self.stdout)
        self.server.register_function(self.stderr)
        self.server.register_function(self.pid)
        self.server.register_function(self.pgid)
        self.server.register_function(self.cpu)

        # Log a warning if libc is not available
        if libc is None:
            log.warning('libc is not available so cannot set PDEATH_SIG in children. Cannot guarantee all children will exit')

    def _preexec(self):
        # Reassign session id to the child process (allows us to kill process group)
        os.setsid()

        # Also set death signal so that processes get SIGKILL if parent terminates unexpectedly
        if libc:
            result = libc.prctl(PR_SET_PDEATHSIG, signal.SIGKILL)
            log.debug('PR_DEATHSIG set to SIGKILL for process {}'.format(os.getpid()))

            if result != 0:
                raise Exception('prctl failed with error code {}'.format(result))

        else:
            log.debug('Could not set PR_DEATHSIG for process {}'.format(os.getpid()))



    def _monitor_cpu(self):

        count = 0
        COUNT_THRESHOLD = 3
        POLLING_INTERVAL = 1.0
        self._stop_monitor = False


        if self.cpu_threshold is None:
            log.error("CPU threshold not set, cant monitor cpu")


        while (True):

            if self._stop_monitor:
                break

            c = self.cpu()

            if c > self.cpu_threshold:
                if count >= COUNT_THRESHOLD:
                    log.info("Restarting service. Reason: continued excess CPU usage")
                    sys.stdout.flush()
                    break

                count += 1
                log.info("Excess CPU usage (%.1f%%) detected. Allowing %d/%d"%(c, count, COUNT_THRESHOLD))
                sys.stdout.flush()



            time.sleep(POLLING_INTERVAL)

        if not self._stop_monitor:
            self.kill()
            time.sleep(1)
            self.start()


    def _get_pipes(self):
        poller = select.poll()
        poller.register(self._p.stdout, select.POLLIN)
        poller.register(self._p.stderr, select.POLLIN)

        scmap = {\
            self._p.stdout.fileno():(self._p.stdout, self._stdout, sys.stdout),
            self._p.stderr.fileno():(self._p.stderr, self._stderr, sys.stderr)}

        while self._p.poll() is None:
            polled = poller.poll(100)
            streams = [scmap[p[0]] for p in polled]

            for stream in streams:
                so = stream[0].readline()[:-1]
                if so:
                    if self._echo:
                        log_output.debug("{}".format(so))

                    self._stdout =  self._stdout[-self.MAX_BUFLEN:]
                    self._stderr =  self._stderr[-self.MAX_BUFLEN:]


        if self._echo:
            log_output.debug("%s"%self._p.stdout.read())
            log_output.debug("%s"%self._p.stderr.read())

        self._p = None

    def _restarter(self):

        while True:

            # start process
            t0 = time.time()
            self._start()

            # Wait for process to die
            self._pthr.join()

            # Check if program died a natural death, and if not restart
            # if the autorestart flag has been set.
            # and only do so if some time has passed (in order to prevent constant
            # restart loops)
            if self._should_still_be_running and self.autorestart and time.time() - t0 > self.MIN_BOOT_TIME:
                log.info("Process stopped unexpectedly, restarting")
                continue
            elif self._should_still_be_running and self.autorestart:
                log.info("Process stopped unexpectedly and too quickly. Waiting {} seconds before trying to restart".format(self.MIN_RESTART_TIME))
                time.sleep(self.MIN_RESTART_TIME)
                continue
            elif self._should_still_be_running:
                log.info("Process stopped unexpectedly")
                break
            elif not self._should_still_be_running:
                log.info("Process stopped expectedly")
                break
            else:
                raise Exception("Unexpected error")

    def start(self):
        self._pthr_starter = threading.Thread(target=self._restarter)
        self._pthr_starter.daemon = True
        self._pthr_starter.start()

    def _start(self):
        if self._p is not None:
            log.error('Process already running')
            return

        self._p = subprocess.Popen(
            self.args,
            bufsize=1,
            stdin=None,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            preexec_fn=self._preexec,
            cwd=None,
            universal_newlines=True,
            )


        self._pthr = threading.Thread(target=self._get_pipes)
        self._pthr.daemon = True
        self._pthr.start()


        if self.cpu_threshold is not None:
            self._pthr_cpumon = threading.Thread(target=self._monitor_cpu)
            self._pthr_cpumon.daemon = True
            self._pthr_cpumon.start()


        self._should_still_be_running = True



    def _ps(self, option):
        ret = subprocess.check_output(["ps", "-p", "%s"%(self.pid()), "-o", option,"--no-headers"])
        return ret.strip()


    def cpu(self):
        return float(self._ps("pcpu"))

    def pid(self):
        return self._p.pid

    def pgid(self):
        return os.getpgid(self._p.pid)

    def kill(self):
        if self._p is None:
            log.error('Process is not running')
            return
        else:
            self._stop_monitor = True
            pgid = self.pgid()
            os.killpg(pgid, signal.SIGTERM)
            self._should_still_be_running = False

            self._pthr.join(timeout=self._kill_timeout)
            if self._pthr.isAlive() :
                log.error("Signal SIGTERM failed to terminate process in {} sec, sending SIGKILL".format(self._kill_timeout))
                os.killpg(pgid, signal.SIGKILL)
                self._pthr.join(timeout=self._kill_timeout)
                if self._pthr.isAlive():
                    log.error("Failed to terminate process, giving up.")
                    return

            self._p = None
            log.info("Servicecontrol is idle")

    def stdout(self):
        if self._p is None:
            log.error('Process is not running')
            return ''
        else:
            return ''.join(self._stdout)


    def stderr(self):
        if self._p is None:
            log.error('Process is not running')
            return ''
        else:
            return ''.join(self._stderr)


def main():
    
    try:
        select.poll
    except:
        print("servicecontrol requires select.poll which is not available", file=sys.stderr)
        print("on your current OS + Python combination.", file=sys.stderr)
        print("Note that on Macos select.poll is not available by default,", file=sys.stderr)
        print("but *is* available in some distributions such as anaconda", file=sys.stderr)
        exit(1)

    #
    # Parse command line
    #
    parser = argparse.ArgumentParser()

    parser.add_argument("--start", action="store_true")
    parser.add_argument("--addr", type=str, default="localhost", help="xmlrpc address, default=localhost")
    parser.add_argument("--port", type=int, default= 9001, help = "xmlrpc port, default=9001")
    parser.add_argument("--no-echo", action="store_true")
    parser.add_argument("--autorestart", action="store_true")
    parser.add_argument("--cpurestart", type=float, help="Set CPU threshold to automatically restart service at")
    parser.add_argument("--log", type=str, help="Filename to log to (default is None - stdout only)" )
    parser.add_argument("--kill-timeout", type=int, default=ServiceControl.DEFAULT_KILL_TIMEOUT, help="Delay to wait after trying to terminate a process before sending SIGKILL, and then before giving up. Default={}".format(ServiceControl.DEFAULT_KILL_TIMEOUT))
    parser.add_argument("--stream-as-log", action="store_true", help="If set, show process output with the normal log formatter. Otherwise show exactly as is")
    parser.add_argument("-i", "--interact", action="store_true")
    parser.add_argument("cmd", help="The command to parse")

    args = parser.parse_args()

    # actual command to run
    import shlex
    argv = shlex.split(args.cmd)

    # Enable logging
    if args.log is not None:
        cf = logging.handlers.TimedRotatingFileHandler(args.log,when='midnight',interval=1,backupCount=0,utc=True)

        if args.stream_as_log:
            formatter = LogFormatter(LogFormatter.DEFAULT_FORMAT)
        else:
            formatter = LogFormatter("child  - %(message)s")

        cf.setFormatter(formatter)
        log.addHandler(cf)
        log_output.addHandler(cf)

    if args.stream_as_log:
        ch_output.setFormatter(LogFormatter(LogFormatter.DEFAULT_FORMAT))
        log_output.addHandler(ch_output)
    else:
        ch_output.setFormatter(LogFormatter("child  - %(message)s"))
        log_output.addHandler(ch_output)


    sc = ServiceControl(argv, addr=args.addr, port=args.port,echo=(not args.no_echo), autorestart=args.autorestart, cputhreshold = args.cpurestart, kill_timeout=args.kill_timeout)

    if args.start is True:
        sc.start()

    if args.interact:
        #
        # Define some wrapper functions to save user having to type sc.xxx
        #
        def kill():
            sc.kill()

        def start():
            sc.start()

        def pid():
            return sc.pid()

        def pgid():
            return sc.pgid()

        def cpu():
            return sc.cpu()

        import code
        code.interact(local=locals())
    else:
        Killer.register_signal(signal.SIGTERM)
        Killer.register_signal(signal.SIGINT)
        while not Killer.kill_now:
            time.sleep(1)

        log.info("SIGTERM or SIGINT received. Killing child and exiting")

    sc.kill()


if __name__ == '__main__':
    main()