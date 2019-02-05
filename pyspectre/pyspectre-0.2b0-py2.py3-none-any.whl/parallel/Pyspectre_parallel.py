import time
import multiprocessing as mp
from .Pyspectre import Pyspectre
from . import Analyses
from fnmatch import fnmatch
import signal


def local_fn(name, self):
    return lambda *args, **kwargs: getattr(Pyspectre, name)(self, *args, **kwargs)


def remote_fn(name, catchfun):
    return lambda *args, **kwargs: catchfun(name, *args, **kwargs)


class Pyspectre_client(Pyspectre):
    # list of regex patterns for functions to ignore:
    functions_to_process_locally = [
    ]

    # list of regex patterns for functions to ignore:
    functions_to_ignore = [
        '__*',
        '_*',
    ]

    def __init__(self, *args, **kwargs):

        kwargs.update({'delayed_start': True})
        super(Pyspectre_client, self).__init__(*args, **kwargs)

        for name in dir(Pyspectre):
            if name not in dir(self) and not any([fnmatch(pattern, name) for pattern in self.functions_to_ignore]):

                obj = getattr(Pyspectre, name)
                if callable(obj):
                    if name in self.functions_to_process_locally:
                        setattr(self, name, local_fn(name, self))
                    else:
                        setattr(self, name, remote_fn(name, self.catchfun))

        # super(Pyspectre_client, self).__init(*args, **kwargs)
        self.inqueue = mp.Queue()
        self.outqueue = mp.Queue()
        self.status = mp.Queue()

        self.server = mp.Process(
            target=Pyspectre_server,
            args=(self.inqueue, self.outqueue, self.status, args, kwargs),
            daemon=True,
        )
        self.server.start()
        self.last_command = None

        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGABRT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def _signal_handler(self, signal, frame):
        if hasattr(self, 'server'):
            try:
                self._cleanup()
            except:
                pass
            try:
                self.server.terminate()
            except:
                self.server.kill(9)
        raise KeyboardInterrupt

    """ THESE FUNCTIONS ARE EXPLICITLY DIFFERENT """

    def _resolve_analysis_type(self):
        self._send_call('resolve_analysis_type', block=True)
        self.analysis_type = self._send_call('get_analysis_type', block=True)

    def _cleanup(self):
        self._send_call('cleanup', block=True)
        self._send_call('STOP', block=False)
        assert self.getlastresult() == 'DEAD', 'could not terminate pyspectre server'

    """ These functions are required for remote evaluation"""

    def catchfun(self, fnname, *args, **kwargs):
        return self._send_call(fnname, *args, **kwargs)

    def _send_call(self, fnname, *args, block=True, **kwargs):
        payload = (fnname, args, kwargs, block) if fnname != 'STOP' else 'STOP'
        self.last_command = fnname
        self.inqueue.put(payload)
        return self.getlastresult() if block else 't'

    def wait(self):
        while self.server.is_alive() and not self.inqueue.empty():
            time.sleep(0.001)
        while self.server.is_alive() and self.is_busy():
            time.sleep(0.001)

    def is_busy(self):
        return False if self.status.empty() else True

    def getlastresult(self):
        self.wait()
        result = self.outqueue.get()
        while not self.outqueue.empty():
            result = self.outqueue.get()
        if result == 'DEAD' and not self.last_command == 'cleanup':
            raise KeyboardInterrupt
        return result

    def flush(self):
        while not self.outqueue.empty():
            _ = self.outqueue.get()

    def isalive(self):
        return self.server.is_alive() if isinstance(self.server, mp.Process) else False

    def is_alive(self):
        return self.isalive()


def Pyspectre_server(inqueue, outqueue, status, args, kwargs):
    try:
        kwargs.update({'delayed_start': False})
        sim = Pyspectre(*args, **kwargs)
        for payload in iter(inqueue.get, 'STOP'):

            status.put(1)
            assert isinstance(payload, tuple) and len(payload) == 4

            fnname = payload[0]
            args = payload[1]
            kwargs = payload[2]
            block = payload[3]

            if fnname in dir(sim) and callable(getattr(sim, fnname)):
                handler = getattr(sim, fnname)
                result = handler(*args, **kwargs)
                if block:
                    outqueue.put(result) if result else outqueue.put('done')

            elif fnmatch(fnname, 'get_*'):
                prop = fnname.split('get_')[-1]
                if hasattr(sim, prop) and not callable(getattr(sim, prop)):
                    outqueue.put(getattr(sim, prop))

            _ = status.get()

        outqueue.put('DEAD')

    except:
        try:
            sim._cleanup()
        except:
            pass
        try:
            outqueue.put('DEAD')
        except:
            pass