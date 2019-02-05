import multiprocessing as mp
from pexpect.replwrap import REPLWrapper
import time


class REPLWrapper_client(object):
    def __init__(self, *replwrapper_args):

        self.inqueue = mp.Queue()
        self.outqueue = mp.Queue()
        self.status = mp.Queue()
        self.replwrapper_args = replwrapper_args

        self.server = mp.Process(
            target=REPLWrapper_server,
            args=(
                self.inqueue,
                self.outqueue,
                self.status,
                self.replwrapper_args
                ),
            daemon=True,
        )
        self.server.start()
        self.pid = self.server.pid
        self.child = self

    def run_command(self, command, block=True):
        return self._send_call('run_command', command, block=block)

    def launch_spectre(self, block=True):
        return self._send_call('launch_spectre', block=block)

    def quit(self):
        try:
            self.run_command('sclQuit', block=False)
            self.wait()
        except:
            pass
        return self._send_call('STOP', block=True)

    def _send_call(self, fnname, args, block=True):
        payload=(fnname, args, block) if fnname != 'STOP' else 'STOP'
        self.inqueue.put(payload)
        return self.getlastresult() if block else 't'

    def wait(self):
        while not self.inqueue.empty():
            time.sleep(0.001)
        while self.is_busy():
            time.sleep(0.001)

    def is_busy(self):
        return False if self.status.empty() else True

    def getlastresult(self):
        self.wait()
        result = self.outqueue.get()
        while not self.outqueue.empty():
            result = self.outqueue.get()
        return result

    def flush(self):
        while not self.outqueue.empty():
            _ = self.outqueue.get()

    def isalive(self):
        return self.server.is_alive() if isinstance(self.server, mp.Process) else False

    def is_alive(self):
        return self.isalive()


def REPLWrapper_server(inqueue, outqueue, status, replwrapper_args):
    for payload in iter(inqueue.get, 'STOP'):

        ## signal busy
        status.put(1)

        ## pull out fn from args
        assert isinstance(payload, tuple) and len(payload)==3
        fnselect = payload[0]
        myargs = payload[1]
        block = payload[2]

        ## define functions:

        if fnselect == 'run_command':
            command=myargs[0]
            result = spectre.run_command(command)
            if block:
                outqueue.put(result)
            else:
                del result

        elif fnselect == 'launch_spectre':
            spectre = REPLWrapper(*replwrapper_args)
            spectre.child.delayafterclose = 0.0
            spectre.child.delaybeforesend = 0.0
            spectre.child.delayafterread = 0.0
            spectre.child.delayafterterminate = 0.0
            if block:
                outqueue.put('t')

        ## remove busy signal
        _ = status.get()

    outqueue.put('DEAD')