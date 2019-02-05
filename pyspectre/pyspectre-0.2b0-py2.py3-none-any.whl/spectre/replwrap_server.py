import multiprocessing as mp
import os


class REPLWrapper_client(object):

    def __init__(self,
                 cmd_or_spawn,
                 orig_prompt,
                 prompt_change=None):

        self.inqueue = mp.Queue(1)
        self.outqueue = mp.Queue(1)

        self.server = mp.Process(
            target=REPLWrapper_server,
            args=(
                self.inqueue,
                self.outqueue,
                cmd_or_spawn,
                orig_prompt,
                prompt_change),
            daemon=True,
        )

        self.server.start()
        self.pid = self.server.pid
        self.child = self
        self._alive = True

    def isalive(self):
        return self._alive

    def run_command(self, command):
        return self._remote_method('run_command', command)

    def terminate(self, force=False):
        return self._remote_method('terminate', force)

    def kill(self, signal):
        return self._remote_method('kill', signal)

    def _remote_method(self, name, *args, **kwargs):
        if self.isalive():
            payload = ('eval_method', (name, args, kwargs))
            self.inqueue.put(payload)
            result = self.outqueue.get()
            if result == 'DEAD':
                self._alive = False
            else:
                return result


def REPLWrapper_server(inqueue, outqueue,
                       cmd_or_spawn,
                       orig_prompt,
                       prompt_change=None):

    from pexpect.replwrap import REPLWrapper

    def try_kill():
        outqueue.put('DEAD')
        if spectre.child.isalive():
            try:
                spectre.child.terminate(force=True)
            except:
                pass
            return

    try:
        spectre = REPLWrapper(
            cmd_or_spawn,
            orig_prompt,
            prompt_change)

        print('successfully launched spectre')
        spectre.child.delayafterclose = 0.0
        spectre.child.delaybeforesend = 0.0
        spectre.child.delayafterread = 0.0
        spectre.child.delayafterterminate = 0.0

        for payload in iter(inqueue.get, 'STOP'):

            if not spectre.child.isalive():
                raise RuntimeError('you asked for something from a dead spectre')

            # pull out fn from args
            assert isinstance(payload, tuple) and len(payload) == 2
            fnselect = payload[0]
            fnargs = payload[1]

            # define functions:
            if fnselect == 'eval_method':
                command = fnargs[0]
                args = fnargs[1]
                kwargs = fnargs[2]
                outqueue.put(getattr(spectre, command)(*args, **kwargs))

    except Exception as e:

        try_kill()

        if 'command' in locals() and command in ['terminate', 'kill']:
            return
        elif 'command' in locals() and command in ['run_command']:
            if 'args' in locals() and args[0] == 'sclQuit()':
                return
        else:
            if spectre is not None:
                print(spectre.child.before)
            raise e

