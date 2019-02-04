from __future__ import print_function

import sys
import gc
import os
import os.path as path
import fnmatch
import argparse
import hashlib
import binascii
import traceback
import threading
import concurrent.futures
import time
import cloudpickle as pickle
import inspect
import pydoc

from random import randint, getrandbits
from netifaces import interfaces, ifaddresses, AF_INET
from concurrent.futures import ThreadPoolExecutor
from socket import gethostname
from collections import OrderedDict
from multiprocessing import cpu_count
from datetime import datetime as DatetimeObj

if sys.version_info.major == 2:
    # for Python2
    from SocketServer import ThreadingMixIn
    from DocXMLRPCServer import DocXMLRPCServer, resolve_dotted_attribute
    from xmlrpclib import ServerProxy, Fault, Binary
    from Tkinter import *  ## notice capitalized T in Tkinter
    from ttk import Notebook
    import tkFileDialog
    import imp
    from socket import error as socketerror

    PY_SYSVER = 2

elif sys.version_info.major == 3:
    # for Python3
    from socketserver import ThreadingMixIn
    from xmlrpc.server import DocXMLRPCServer, resolve_dotted_attribute
    from xmlrpc.client import ServerProxy, Fault, Binary
    from tkinter import *  ## notice lowercase 't' in tkinter here
    from tkinter.ttk import Notebook
    from tkinter import filedialog as tkFileDialog
    import importlib

    PY_SYSVER = 3

iflist = {'all': '0.0.0.0'}
for interface in interfaces():
    config = ifaddresses(interface)
    # AF_INET is not always present
    if AF_INET in config.keys():
        for link in config[AF_INET]:
            # loopback holds a 'peer' instead of a 'broadcast' address
            # if 'addr' in link.keys() and 'peer' not in link.keys():
            if 'addr' in link.keys():
                iflist.update({str(interface): link['addr']})
del interface

# set log-level for servers:
# logging.getLogger("requests").setLevel(logging.WARNING)

default_port = 11234
default_interface = 'all'
default_remote_ips = (('143.215.156.66', default_port),)
default_password = 'ratsofftoya'
default_notify_interval = 3 * 60
default_poll_interval = 1 * 60
default_max_outstanding_challenges = 5
default_challenge_ttl = 60
default_max_challenge_retries = 3
default_challenge_retry_interval = 3
default_job_queue_size = 100
default_max_n_workers = cpu_count()
default_verbosity = 1

thisfile = os.path.abspath(__file__)
thispath = os.path.split(thisfile)[0]

if PY_SYSVER == 3:
    rpcable_types = (bool, int, float, str, list, tuple, dict, DatetimeObj, type(None), bytes, bytearray)
else:
    rpcable_types = (bool, int, float, str, list, tuple, dict, DatetimeObj, type(None), bytes, bytearray, unicode)


def rpcable(item):
    if not isinstance(item, rpcable_types):
        return False

    elif isinstance(item, (list, tuple)):
        for it in item:
            if not rpcable(it):
                return False

    elif isinstance(item, dict):
        for value in item.values():
            if not rpcable(value):
                return False

    return True


class SecureMethodServer(object):
    def __init__(self, waverunner_server):
        self.fns = {}
        self.waverunner_server = waverunner_server

    def _get_method_argstring(self, method_name):
        ind = [item[0] for item in self.waverunner_server._local_methods].index(method_name)
        fn = self.waverunner_server._local_methods[ind][1]
        spec = inspect.getargspec(fn)
        return inspect.formatargspec(*spec)

    def _methodHelp(self, method_name):
        ind = [item[0] for item in self.waverunner_server._local_methods].index(method_name)
        fn = self.waverunner_server._local_methods[ind][1]
        return pydoc.getdoc(fn)

    def _listMethods(self):
        return self.fns.keys()

    def _dispatch(self, name, params):

        if name in self.fns:
            return self.fns[name](*params)

        else:
            return 'did not find that method'

    def _register(self, name, fn):
        self.fns.update({name: fn})


def PublicMethod(fn):
    setattr(fn, '_waverunner_public', True)
    return fn


def SecureMethod(fn):
    setattr(fn, '_waverunner_public', False)
    return fn


# def PublicInstance(instance):
#     setattr(instance, '_waverunner_public', True)
#     return instance
#
#
# def SecureInstance(instance):
#     setattr(instance, '_waverunner_public', False)
#     return instance


def _file2mod(filepath):
    return os.path.split(filepath)[-1].split('.py')[0]


def _list_modules_at_path(pathspec, names=None):
    assert os.path.isdir(pathspec)
    mods = [file.split('.')[0] for file in fnmatch.filter(os.listdir(pathspec), '[!_]*.py')]
    mods.sort()
    mods = list(filter(lambda item: item in names, mods)) if names else mods
    paths = [path.join(pathspec, mod + '.py') for mod in mods]
    return tuple(zip(mods, paths))


def _get_live_module(module_path):
    module_name = _file2mod(module_path)
    if module_name not in sys.modules:
        if PY_SYSVER == 2:
            module = imp.load_source(module_name, module_path)
        else:
            module = importlib.import_module(module_name)
    module = sys.modules[module_name]
    return module


def _execute_fn(int_fn, args, kwargs):
    import cProfile

    result = None
    args = [] if args is None else args
    kwargs = {} if kwargs is None else kwargs

    # if args is None and kwargs is None:
    #     result = int_fn()
    # if args is not None and kwargs is None:
    #     result = int_fn(*args)
    # elif args is None and kwargs is not None:
    #     result = int_fn(**kwargs)
    # elif args is not None and kwargs is not None:
    #     result = int_fn(*args, **kwargs)

    # return cProfile.runctx('int_fn(*args, **kwargs)', filename='test', locals=locals(), globals=globals())
    try:
        return int_fn(*args, **kwargs)

    except Exception as e:
        return e


class OutOfChallengesError(RuntimeError):
    pass


if PY_SYSVER == 3:

    NoWaverunnerThereError = (ConnectionError, ConnectionRefusedError)

elif PY_SYSVER == 2:

    NoWaverunnerThereError = (socketerror, )


class MaxRetriesError(RuntimeError):
    pass


class ChallengeNotValidError(RuntimeError):
    pass


class ConflictingHostError(RuntimeError):
    pass


class JobQueueEmpty(RuntimeError):
    pass


class JobNotPendingError(RuntimeError):
    pass


class Client(threading.local):
    def __init__(self):
        self.address = None


class Job(object):
    def __init__(self, func, args=[], kwargs={}, host=None, timeout=None, completion_hook=None):
        self.host = str(host)
        self.fn = str(func)

        if isinstance(args, str):
            args = [args]
        if isinstance(args, tuple):
            args = list(args)
        if kwargs:
            assert isinstance(kwargs, dict), 'provided kwargs must be a dict'

        # pickled_args = None
        # if args and len(args) > 0:
        #     pickled_args = [False]*len(args)
        #     for i, arg in enumerate(args):
        #         if not rpcable(arg):
        #             pickled_args[i] = True
        #             args[i] = pickle.dumps(args[i])
        #
        # pickled_kwargs = None
        # if kwargs and len(kwargs) > 0:
        #     pickled_kwargs = [False]*len(kwargs)
        #     for i, arg in kwargs.items():
        #         if not rpcable(arg):
        #             pickled_kwargs[i] = True
        #             kwargs[i] = pickle.dumps(args[i])

        self.args = tuple(args) if args else None
        self.kwargs = tuple((key, val) for key, val in kwargs.items()) if kwargs else None
        # self.pickling = {'args': pickled_args,
        #                  'kwargs': pickled_kwargs,
        #                  'result': None}
        self.timeout = int(timeout) if timeout is not None and timeout >= 0 else None
        self.creation_time = time.time()
        self.start_time = None
        self.completed_time = None
        self.id = str(hash(self))
        self.result = None
        self.completion_hook = completion_hook if completion_hook and callable(completion_hook) else None

    def __hash__(self):
        # ll = []
        # if self.args:
        #     for arg in self.args:
        #         try:
        #             ll.append(hash(arg))
        #         except:
        #             if hasattr(arg, 'ravel'):
        #                 ll.append(hash(tuple(arg.ravel())))
        #
        # if self.kwargs:
        #     for arg in self.kwargs:
        #         try:
        #             ll.append(hash(arg))
        #         except:
        #             if hasattr(arg, 'ravel'):
        #                 ll.append(hash(tuple(arg.ravel())))

        hash = hashlib.sha1()

        # hash.update(bytes(self.host))
        hash.update(self.fn.encode('utf-8'))
        hash.update(str(self.args).encode('utf-8'))
        hash.update(str(self.kwargs).encode('utf-8'))
        # hash.update(bytes(self.creation_time))

        # return hash((
        #     hash(self.host),
        #     hash(self.fn),
        #     hash(tuple(ll)),
        #     hash(self.creation_time)
        # ))

        return int(hash.hexdigest()[:16], 16)

    def pack(self):
        return PackedJob(self)


class PackedJob(object):
    def __init__(self, job):
        self.id = job.id
        self.method = job.fn
        self.has_completion_hook = True if job.completion_hook is not None and callable(job.completion_hook) else False
        self.creation_time = job.creation_time
        self.start_time = job.start_time
        self.ttl = job.timeout
        self.competed_time = job.completed_time
        self.host = job.host
        self.data = pickle.dumps(job)
        self.result = None

    def unpack(self):
        unwrapped = pickle.loads(self.data)
        unwrapped.start_time = self.start_time
        unwrapped.completed_time = self.competed_time
        unwrapped.result = self.result
        return unwrapped


class ThreadingRPCServer(ThreadingMixIn, DocXMLRPCServer, object):
    def __init__(self, *args, **kwargs):
        super(ThreadingRPCServer, self).__init__(*args, **kwargs)
        self.client = Client()
        self.lock = threading.Lock()

    def process_request_thread(self, request, client_address):
        # self.lock.acquire()
        self.client.address = client_address
        return super(ThreadingRPCServer, self).process_request_thread(request, client_address)

    # def _dispatch(self, method, params):
    #     """Dispatches the XML-RPC method.
    #
    #     This is monkeypatched from the source.
    #     Releasing the lock only in order to run the external code.
    #     """
    #     try:
    #         # call the matching registered function
    #         func = self.funcs[method]
    #     except KeyError:
    #         pass
    #     else:
    #         if func is not None:
    #             return func(*params)
    #         raise Exception('method "%s" is not supported' % method)
    #
    #     if self.instance is not None:
    #         if hasattr(self.instance, '_dispatch'):
    #             # call the `_dispatch` method on the instance
    #             self.lock.release()
    #             return self.instance._dispatch(method, params)
    #
    #         # call the instance's method directly
    #         try:
    #             func = resolve_dotted_attribute(
    #                 self.instance,
    #                 method,
    #                 self.allow_dotted_names
    #             )
    #         except AttributeError:
    #             pass
    #         else:
    #             if func is not None:
    #                 self.lock.release()
    #                 return func(*params)
    #
    #     raise Exception('method "%s" is not supported' % method)


class RPCServer(DocXMLRPCServer, object):
    def __init__(self, *args, **kwargs):
        super(RPCServer, self).__init__(*args, **kwargs)
        self.client = Client()

    def process_request(self, request, client_address):
        self.client.address = client_address
        return super(RPCServer, self).process_request(request, client_address)


class HookedDict(dict):
    def __init__(self, hookfn, *args, **kwargs):
        super(HookedDict, self).__init__(*args, **kwargs)
        self.hook = hookfn

    def __setitem__(self, *args, **kwargs):
        super(HookedDict, self).__setitem__(*args, **kwargs)
        self.hook()

    def update(self, *args, **kwargs):
        super(HookedDict, self).update(*args, **kwargs)
        self.hook()


def _get_challenge_gen_response(remote_host, password, max_retries=3, retry_interval=1.1, event_timer=None):

    if isinstance(remote_host, str):
        remote_host = remote_host.split(':')
        if len(remote_host) == 1:
            remote_host = (remote_host, default_port)

        host = ServerProxy('http://{}:{}'.format(remote_host[0], remote_host[1]))

    elif isinstance(remote_host, ServerProxy):
        host = remote_host

    else:
        raise ValueError('unrecognized host format. Try \'examplehost:11234\'')

    retry_ct = 0
    response = None

    try:
        while retry_ct < max_retries:
            challenge = host.get_challenge()
            response, salt = _generate_response(challenge, password)
            break

    except OutOfChallengesError:
        print('server was out of challenges')
        retry_ct += 1
        if event_timer:
            event_timer.wait(retry_interval)
        else:
            time.sleep(retry_interval)
        pass

    if response is None:
        raise MaxRetriesError("couldn't get a challenge and ran out of retries")

    return response, salt


def _generate_response(challenge, password, salt=None):
    salt = format(getrandbits(256), 'x').encode() if salt is None else salt
    salt = salt.encode('utf-8') if isinstance(salt, str) else salt

    key = binascii.hexlify(bytes(
        hashlib.pbkdf2_hmac(
            'sha1',
            password.encode(),
            salt=salt,
            iterations=1000)))

    return hashlib.sha1(key + challenge.encode()).hexdigest(), salt


def external_request(remote_host, remote_fn_name, args=None, kwargs=None,
                     password=default_password,
                     thread_lock=None, event_timer=None,
                     max_retries=default_max_challenge_retries,
                     retry_interval=default_challenge_retry_interval,
                     verbosity=default_verbosity):

    if not isinstance(remote_host, (list, tuple)):
        remote_host = str(remote_host)
        remote_host = remote_host.split(':')

    if len(remote_host) < 2:
        if remote_host[0].isdigit():
            remote_host = (default_remote_ips, remote_host[0])
        else:
            remote_host = (remote_host[0], default_port)

    if args:
        if not rpcable(args):
            args = ('pickled_args', Binary(pickle.dumps(args)))
        else:
            args = ('args', tuple(args))

    if kwargs:
        if not rpcable(kwargs):
            kwargs = ('pickled_kwargs', Binary(pickle.dumps(kwargs)))
        else:
            kwargs = ('kwargs', kwargs)

    host = ServerProxy('http://{}:{}'.format(remote_host[0], remote_host[1]))

    secure = host.is_secure(remote_fn_name)

    if secure is None:
        print('remote host did not recognize that fn: {}'.format(remote_fn_name))
        return None

    if secure is True:

        if thread_lock:
            with thread_lock:
                print('got challenge acquisition lock') if verbosity > 1 else None
                response, salt = _get_challenge_gen_response(
                    host,
                    password,
                    max_retries,
                    retry_interval,
                    event_timer)
        else:
            response, salt = _get_challenge_gen_response(
                host,
                password,
                max_retries,
                retry_interval,
                event_timer)

        print('got a challenge. calling remote fn: {}'.format(remote_fn_name)) if verbosity > 1 else None

    fn_args = []
    if secure:
        fn_args.append((response, salt))
    if args:
        fn_args.append(args)
    if kwargs:
        fn_args.append(kwargs)

    print('calling remote fn: {}'.format(remote_fn_name)) if verbosity > 1 else None

    result = getattr(host, remote_fn_name)(*fn_args)

    if isinstance(result, (list, tuple)) and len(result) == 2 and result[0] == 'pickled_data':
        d = result[1].data if hasattr(result[1], 'data') else result[1]
        result = pickle.loads(d)

    print('result={}'.format(result)) if verbosity >= 5 else None

    if remote_fn_name == 'put_job':
        # i just dropped off a job... do garbage collection
        gc.collect()

    return result


class Waverunner(object):

    def __init__(self,
                 port=default_port,
                 interface=default_interface,
                 remote_ips=default_remote_ips,
                 path_to_serve=None,
                 password=default_password,
                 notify_interval=default_notify_interval,
                 polling_interval=default_poll_interval,
                 max_outstanding_challenges=default_max_outstanding_challenges,
                 challenge_ttl=default_challenge_ttl,
                 max_challenge_retries=default_max_challenge_retries,
                 challenge_retry_interval=default_challenge_retry_interval,
                 max_jobs_queued=default_job_queue_size,
                 max_n_workers=default_max_n_workers,
                 worker_processes=False,
                 verbosity=1,
                 ):

        # user-facing
        self.password = str(password) if password is not None else default_password
        self.verbosity = verbosity

        if notify_interval is None:
            self.notify_interval = 0
        else:
            self.notify_interval = int(notify_interval) if int(notify_interval) >= 0 else default_notify_interval

        if polling_interval is None:
            self.polling_interval = 0
        else:
            self.polling_interval = int(polling_interval) if polling_interval >= 0 else default_poll_interval

        if remote_ips is None:
            if notify_interval is not None or polling_interval is not None:
                self._remote_ips = default_remote_ips
        else:
            self._remote_ips = self._parse_remote_ip_spec(remote_ips)

        # semi-user-facing
        #     these have access methods, getters, setters, etc
        self._port = int(port) if port is not None else default_port

        if interface:
            if interface in iflist.keys():
                self._iface = interface
                self._ip = iflist[interface]

            else:
                raise RuntimeError('could not find that interface')

        else:
            self._iface = default_interface
            self._ip = iflist[default_interface]

        self._srv_path = None

        #     these are just a little bit more obscure parameters
        self._max_outstanding_challenges = max_outstanding_challenges if 0 < max_outstanding_challenges < 50 else 2
        self._max_challenge_retries = max_challenge_retries
        self._challenge_retry_interval = challenge_retry_interval
        self._challenge_ttl = int(challenge_ttl)
        self._bookkeeper_interval = 15
        self._max_jobs_queued = max_jobs_queued


        # workers
        self._worker_processes = True if worker_processes else False
        self._max_n_workers = max_n_workers if max_n_workers > 0 else 2 * cpu_count()

        if self._worker_processes:
            self._worker_pool = concurrent.futures.ProcessPoolExecutor(max_workers=self._max_n_workers)
        else:
            self._worker_pool = concurrent.futures.ThreadPoolExecutor(max_workers=self._max_n_workers
                                                                      )
        # threading
        self._server_thread = None
        self._bookkeeper_thread = None
        self._poll_remote_hosts_thread = None
        self._notify_server_thread = None

        self._events = {
            'stop_notify': threading.Event(),
            'stop_polling': threading.Event(),
            'stop_bookkeeper': threading.Event(),
            'shutdown': threading.Event(),
        }

        self._events['stop_notify'].set()
        self._events['stop_polling'].set()
        self._events['stop_bookkeeper'].set()
        self._events['shutdown'].clear()

        self._threadlocks = {
            'server_challenge': threading.Lock(),
            'client_challenge': threading.Lock(),
            'jobqueue': threading.Lock(),
            'put_results': threading.Lock()}

        # self._worker_sem = threading.BoundedSemaphore(self._max_n_workers)

        # xmlrpc
        self._server = None
        self._serving = False
        self._srv_methods = []
        self._srv_methods_secured = []
        self._secure_method_server = SecureMethodServer(self)
        # self._srv_instances = []
        # self._srv_instances_secured = []

        # internal services
        self._registered_services = HookedDict(self._update_gui_vars)
        self._local_methods = []
        # self._local_instances = []
        self._host_file = traceback.extract_stack(limit=2)[-2][0]
        self._host_path = os.path.split(self._host_file)
        self._outstanding_challenges = {}
        self._job_queues = {}
        self._pending_jobs = {}
        self._completed_jobs = {}
        self._tkroot = None
        self._rtvars = None

        if path_to_serve is not None:
            self.set_testpath(path_to_serve)

    def __enter__(self):
        self.start_service()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop_service()
        self.exit_gracefully()
        del self

    @staticmethod
    def _parse_remote_ip_spec(remote_ips):

        if isinstance(remote_ips, int):
            remote_ips = [str(remote_ips)]

        elif isinstance(remote_ips, str):
            if ',' in remote_ips:
                remote_ips = [item.strip() for item in remote_ips.split(',')]
            elif ' ' in remote_ips:
                remote_ips = [item.strip() for item in remote_ips.split(' ')]
            else:
                remote_ips = [remote_ips]

        parsed = []
        for i, user in enumerate(list(remote_ips)):
            if isinstance(user, str):
                user = user.split(':')
            if len(user) == 1:
                if user[0].isdigit():
                    # port on localhost
                    user = ('127.0.0.1', int(user[0]))
                else:
                    user = (user[0].strip('\''), default_port)
            elif len(user) == 2:
                user = (user[0].strip('\''), int(user[1]))
            parsed.append(tuple(user))

        return tuple(parsed) if parsed else None

    @property
    def port(self):
        return self._port

    @property
    def srv_path(self):
        return self._srv_path

    @property
    def ip(self):
        return self._ip

    @property
    def iface(self):
        return self._iface

    @property
    def registered_services(self):
        return self._registered_services

    @property
    def remote_ips(self):
        return self._remote_ips

    @property
    def known_services(self):
        return tuple([item[0] for item in self._srv_methods + self._srv_methods_secured])

    @port.setter
    def port(self, value):
        self._set_port(value)

    @srv_path.setter
    def srv_path(self, value):
        self._set_srv_path(value)

    @ip.setter
    def ip(self, value):
        self._set_ip(value)

    @iface.setter
    def iface(self, value):
        self._set_iface(value)

    @remote_ips.setter
    def remote_ips(self, value):
        self._set_remote_ips(value)

    def _set_port(self, value):
        self._port = int(value)
        if self._rtvars is not None:
            self._rtvars['port'].set(str(self._port))

    def _set_srv_path(self, value):
        self._srv_path = str(value)
        if self._rtvars is not None:
            self._rtvars['srv_path'].set(self._srv_path)

    def _set_ip(self, value):
        self._ip = str(value)
        if self._rtvars is not None:
            self._rtvars['ip'].set(str(self._ip))

    def _set_iface(self, value):

        if value not in iflist.keys():
            print('that is not a valid interface. ignoring')
            return

        else:
            self._iface = str(value)
            serving = self._serving

            if serving:
                self.stop_service()

            self._ip = iflist[value]

            if serving:
                self.start_service()

            if self._rtvars is not None:
                self._rtvars['iface'].set(self._iface)

            return

    def _set_remote_ips(self, value):
        self._remote_ips = self._parse_remote_ip_spec(value)

    def _update_gui_vars(self):
        if self._rtvars is not None:
            for gui_var in self._rtvars.keys():
                self._rtvars[gui_var].set(getattr(self, gui_var))

    @PublicMethod
    def is_secure(self, fn):
        if fn in [name for name, _ in self._srv_methods_secured]:
            return True
        elif fn in [name for name, _ in self._srv_methods]:
            return False
        else:
            print('Server.is_secure(): could not find function named {}'.format(fn)) if self.verbosity >2 else None
            return None

    @PublicMethod
    def get_challenge(self):
        with self._threadlocks['server_challenge']:

            if len(self._outstanding_challenges) >= self._max_outstanding_challenges:
                print('ran out of challenges') if self.verbosity > 0 else None
                raise OutOfChallengesError

            else:
                client = self._server.client.address[0] if self._server.client.address is not None else 'local'
                challenge = ''.join([format(randint(0, 16), 'x') for i in range(256)])

                if client in self._outstanding_challenges:
                    self._outstanding_challenges[client].append((challenge, time.time()))
                else:
                    self._outstanding_challenges.update({client: [(challenge, time.time())]})

                print('issued a challenge') if self.verbosity > 1 else None
                return challenge

    @PublicMethod
    def notify(self, address, port, bare_fns, bare_insts, sec_fns, sec_insts):

        self.registered_services.update({
            ':'.join([address, str(port)]): [bare_fns, bare_insts, sec_fns, sec_insts],
        })
        print('got a notification from {}:{}'.format(address, port)) if self.verbosity > 2 else None

        return '10-4'

    def queue_request(self, *args, **kwargs):
        return self.queue_job(self, *args, **kwargs)

    def queue_job(self, method_name, args=None, host=None, kwargs=None, timeout=None, completion_hook=None):
        if not method_name:
            print("attempted to queue an empty job. ignoring.")
            return None

        if host is None:
            host = ''

        job = Job(method_name, args, kwargs, host=host, timeout=timeout, completion_hook=completion_hook)

        with self._threadlocks['jobqueue']:
            if job.host not in self._job_queues:
                self._job_queues.update({job.host: OrderedDict()})
            self._job_queues[job.host].update({
                job.id: job.pack()
            })

        print('job queued') if self.verbosity > 1 else None
        return job.id

    @SecureMethod
    def get_job_list(self):
        host, port = self._server.client.address
        joblist = []

        if host in self._job_queues and self._job_queues[host]:
            joblist.extend(list(self._job_queues[host].values()))

        if '' in self._job_queues and self._job_queues['']:
            joblist.extend(list(self._job_queues[''].values()))

        print('sending list of {} potential jobs to {}'.format(len(joblist), host)) if self.verbosity > 2 else None
        return tuple([(item.id, item.method) for item in joblist])

    @SecureMethod
    def get_job(self, job_id):

        host, port = self._server.client.address
        job = None

        with self._threadlocks['jobqueue']:

            if host in self._job_queues and job_id in self._job_queues[host]:
                job = self._job_queues[host][job_id]
                job.start_time = time.time()
                self._pending_jobs.update({job_id: job})
                del self._job_queues[host][job_id]

            elif '' in self._job_queues and job_id in self._job_queues['']:
                job = self._job_queues[''][job_id]
                job.start_time = time.time()
                self._pending_jobs.update({job_id: job})
                del self._job_queues[''][job_id]

            if isinstance(job, PackedJob):
                print('giving job {} to {}'.format(job_id, host))
                return job
            else:
                raise JobQueueEmpty

    @SecureMethod
    def put_job(self, job_id, result, success):

        if job_id not in self._pending_jobs:
            raise JobNotPendingError

        print('trying to get threadlock on jobqueue...') if self.verbosity > 2 else None
        with self._threadlocks['jobqueue']:

            print('got threadlock on jobqueue...') if self.verbosity > 2 else None

            if not success:
                print('job {} failed; putting it back on the queue.'.format(job_id)) if self.verbosity > 0 else None
                j = self._pending_jobs[job_id]
                del self._pending_jobs[job_id]
                j.start_time = None
                self._job_queues[j.host].update({j.id: j})
                return 'thanks for being a friend'

            else:
                print('received a completed job') if self.verbosity > 0 else None
                j = self._pending_jobs[job_id]
                del self._pending_jobs[job_id]

                j.comlpeted_time = time.time()
                j.result = result
                self._completed_jobs.update({j.id: j})

                if j.has_completion_hook:
                    hook = j.unpack().completion_hook

                    try:
                        hook(j)

                    except Exception as e:
                        print(e)
                        pass

                gc.collect()
                return '10-4'

    def get_result(self, job, timeout=None):

        if hasattr(job, 'id'):
            # assume it's an id
            id = job.id

        elif isinstance(job, str):
            id = job

        t = 0
        while id not in self._completed_jobs and not self._events['shutdown'].set():
            self._events['shutdown'].wait(1)
            t += 1
            if timeout and t > timeout:
                break
        try:
            rjob = self._completed_jobs[id]
            return rjob.result

        except KeyError:
            return None

        finally:
            gc.collect()

    def wait_for_job(self, job_id, timeout=None):
        start = time.time()

        while job_id in self._pending_jobs:
            self._events['shutdown'].wait(1)
            age = time.time() - start
            if timeout and age > timeout:
                return None

    def block_for_queue(self, timeout=None):
        start = time.time()

        while len(self._pending_jobs) + sum([len(q) for q in self._job_queues.values()]) > 0:
            self._events['shutdown'].wait(1)
            age = time.time() - start
            if timeout and age > timeout:
                print('TIMEOUT!!!!!!!!!!!!!!!!!!!')
                return None

    def notify_remote(self, ip, port):
        try:
            print('about to notify {}:{}'.format(ip, port)) if self.verbosity > 1 else None
            self.external_request(
                (ip, port),
                'notify',
                self.ip, self.port,
                [name for name, _ in self._srv_methods],
                [name for name, _ in self._srv_methods_secured],
            )
            print('notified {}:{}'.format(ip, port)) if self.verbosity > 1 else None

        except NoWaverunnerThereError:
            pass

    def _notify_remotes_forever(self):
        if not self._remote_ips or self.notify_interval == 0 or self.notify_interval is None:
            return

        print('user notification thread launched') if self.verbosity > 1 else None

        while not self._events['stop_notify'].is_set() and not self._events['shutdown'].is_set():
            print('starting a round of notifications') if self.verbosity > 1 else None

            for ip, port in self._remote_ips:

                if (ip == self.ip or ip == '127.0.0.1' or ip == 'localhost') and port == self.port:
                    continue

                else:
                    self.notify_remote(ip, port)

            self._events['stop_notify'].wait(timeout=self.notify_interval)

    def poll_remotes(self):

        print('starting a round of polling') if self.verbosity > 1 else None

        id = None

        for ip, port in self._remote_ips:
            if (ip == self.ip or ip == 'localhost' or ip == '127.0.0.1') and port == self.port:
                continue

            while True:
                # n_busy_workers = len(self._worker_threads)
                # if n_busy_workers >= self._max_n_workers:
                #     return

                if not self._worker_processes:
                    queue_full = not self._worker_pool._work_queue.empty()

                    # if hasattr(self._worker_pool, '_threads'):
                    #     queue_full = not self._worker_pool._work_queue.empty()
                    #
                    # else:
                    #     if self._worker_pool._work_queue.not_full.acquire():
                    #         queue_full = False
                    #         self._worker_pool._work_queue.not_full.release()
                    #     else:
                    #         queue_full = True

                else:
                    queue_full = len(self._worker_pool._pending_work_items) > 0

                if queue_full:
                    print('all workers busy') if self.verbosity >=3 else None
                try:
                    print('about to poll {}:{}'.format(ip, port)) if self.verbosity > 1 else None

                    l = self.external_request((ip, port), 'get_job_list')

                    if l:
                        matches = [job[0] for job in l if job[1] in self.known_services]
                        if matches:
                            j_id = matches[0]
                        else:
                            j_id = None
                    else:
                        break

                    if j_id:
                        j = self.external_request((ip, port), 'get_job', j_id)
                    else:
                        break

                    if isinstance(j, PackedJob):
                        j = j.unpack()
                    else:
                        break

                except NoWaverunnerThereError:
                    break

                except Fault as err:
                    if 'JobQueueEmpty' in err.faultString:
                        break
                    else:
                        raise err

                if isinstance(j, Job):
                    print('got a job from {}'.format(ip))
                    secure = self.is_secure(j.fn)

                    if secure is None:
                        print('i cannot run this job')
                        self.external_request((ip, port), 'put_job', id, 'FAILED', False)

                    else:
                        self._launch_worker_thread(j, ip, port)

    def _poll_remotes_forever(self):

        if not self._remote_ips or self.polling_interval == 0 or self.polling_interval is None:
            return

        print('polling thread launched') if self.verbosity > 1 else None
        while \
            not self._events['stop_polling'].is_set() \
            and not self._events['shutdown'].is_set() \
            and self._remote_ips \
            and self.polling_interval:

            self.poll_remotes()
            self._events['stop_polling'].wait(timeout=self.polling_interval)

    def _launch_worker_thread(self, job, ip, port):

        args = job.args
        kwargs = job.kwargs

        int_fn = None
        for name, fn in self._local_methods:
            if name == job.fn:
                int_fn = fn
                break

        # print('int_fn: {}, int_fn.__name__: {}'.format(int_fn, int_fn.__name__)) \
        #     if self.verbosity > 3 else None

        def handle_result(job, ip, port, result):

            # self._worker_sem.acquire()
            print('result: {}'.format(result)) if self.verbosity > 3 else None
            if not isinstance(result, Exception):

                try:
                    with self._threadlocks['put_results']:
                        self.external_request((ip, port), 'put_job', job.id, result, True)

                except Fault as e:
                    if 'JobNotPendingError' in e.faultString:
                        print(e)

                except socketerror:
                    print('remote host disappeared')

            else:

                if isinstance(job, Job):
                    job = job.pack()

                try:
                    with self._threadlocks['put_results']:
                        self.external_request((ip, port), 'put_job', job.id, 'FAILED', False)

                except Fault as e:
                    if 'JobNotPendingError' in e.faultString:
                        print(e)

                except socketerror:
                    print('remote host disappeared')

            # finally:
            #     self._worker_sem.release()
            #     self._worker_threads.remove(threading.current_thread())

        future_result = self._worker_pool.submit(_execute_fn, int_fn, args, kwargs)
        print('submitted job to worker') if self.verbosity >= 2 else None
        future_result.add_done_callback(
            lambda future, job=job, ip=ip, port=port: handle_result(job, ip, port, future.result())
        )

        # t = multiprocessing.Process(name='worker', target=execute,
        #                      args=(job, ip, port))
        # t.daemon = True
        # t.start()
        # self._worker_threads.append(t)

    def _generate_response(self, challenge, salt=None):
        salt = format(getrandbits(256), 'x').encode() if salt is None else salt
        salt = salt.encode('utf-8') if isinstance(salt, str) else salt

        key = binascii.hexlify(bytes(
            hashlib.pbkdf2_hmac(
                'sha1',
                self.password.encode(),
                salt=salt,
                iterations=1000)))

        return hashlib.sha1(key + challenge.encode()).hexdigest(), salt

    def threaded_external_requests(self, hosts, fn_names, args=None, kwargs=None, timeout=5 * 60):

        with ThreadPoolExecutor(max_workers=100) as E_daddy:
            if args is None and kwargs is None:
                futures = E_daddy.map(self.external_request, hosts, fn_names, timeout=timeout)
            elif args is not None and kwargs is None:
                futures = E_daddy.map(self.external_request, hosts, fn_names, args, timeout=timeout)
            elif args is None and kwargs is not None:
                futures = E_daddy.map(self.external_request, hosts, fn_names, kwargs, timeout=timeout)
            else:
                futures = E_daddy.map(self.external_request, hosts, fn_names, args, kwargs, timeout=timeout)

            results = []
            for i in futures:
                results.append(i)
            return results

    def external_request(self, remote_host, remote_fn_name, *args, **kwargs):
        """
                     remote_host, remote_fn_name, args=None, kwargs=None,
                     password=default_password,
                     thread_lock=None, event_timer=None,
                     max_retries=default_max_challenge_retries,
                     retry_interval=default_challenge_retry_interval,
                     verbosity=default_verbosity
        :param remote_host:
        :param remote_fn_name:
        :param args:
        :param kwargs:
        :return:
        """
        return external_request(
            remote_host=remote_host,
            remote_fn_name=remote_fn_name,
            args=args,
            kwargs=kwargs,
            password=self.password,
            thread_lock=self._threadlocks['client_challenge'],
            event_timer=self._events['shutdown'],
            max_retries=self._max_challenge_retries,
            retry_interval=self._challenge_retry_interval,
            verbosity=self.verbosity
        )

    # def external_request(self, remote_host, remote_fn_name, *args, **kwargs):
    #
    #     if isinstance(remote_host, str):
    #         remote_host = remote_host.split(':')
    #     if len(remote_host) < 2:
    #         remote_host = [remote_host, default_port]
    #
    #     host = ServerProxy('http://{}:{}'.format(remote_host[0], remote_host[1]))
    #
    #     secure = host.is_secure(remote_fn_name)
    #
    #     if secure is not None:
    #         if args and not rpcable(args):
    #             args = ('pickled_data', Binary(pickle.dumps(args)))
    #         if kwargs and not rpcable(kwargs):
    #             kwargs = ('pickled_data', Binary(pickle.dumps(kwargs)))
    #
    #     if secure is True:
    #
    #         with self._threadlocks['client_challenge']:
    #             print('got challenge acquisition lock') if self.verbosity > 1 else None
    #             retry_ct = 0
    #             response = None
    #
    #             try:
    #                 while retry_ct < self._max_challenge_retries:
    #                     challenge = host.get_challenge()
    #                     response, salt = self._generate_response(challenge)
    #                     break
    #
    #             except OutOfChallengesError:
    #                 print('server was out of challenges')
    #                 retry_ct += 1
    #                 self._events['shutdown'].wait(self._challenge_retry_interval)
    #                 pass
    #
    #             if response is None:
    #                 raise MaxRetriesError("couldn't get a challenge and ran out of retries")
    #
    #     if secure is True and response is not None:
    #         print('got a challenge. calling remote fn: {}'.format(remote_fn_name)) if self.verbosity > 1 else None
    #         result = host.__getattr__(remote_fn_name)((response, salt), *args, **kwargs)
    #
    #     elif secure is False:
    #         print('calling public remote fn: {}'.format(remote_fn_name)) if self.verbosity > 1 else None
    #         result = host.__getattr__(remote_fn_name)(*args, **kwargs)
    #
    #     elif secure is None:
    #         print('remote host did not recognize that fn: {}'.format(remote_fn_name))
    #         result = None
    #
    #     if isinstance(result, (list, tuple)) and len(result) == 2 and result[0] == 'pickled_data':
    #         d = result[1].data if hasattr(result[1], 'data') else result[1]
    #         result = pickle.loads(d)
    #
    #     print('result={}'.format(result)) if self.verbosity >= 5 else None
    #
    #     if remote_fn_name == 'put_job':
    #         # i just dropped off a job... do garbage collection
    #         gc.collect()
    #
    #     return result

    def _external_base_wrapper(self, fn):

        def wrapped(*args):
            try:
                client = self._server.client.address[0] if self._server.client.address is not None else 'local'
                print('handling request for basic function by client {}'.format(client)) if self.verbosity > 2 else None

                fn_args = []
                kwargs = {}

                for arg_i in args:

                    if isinstance(arg_i, (list, tuple)) and len(arg_i) == 2 and arg_i[0] == 'args':
                        fn_args = arg_i[1]

                    elif isinstance(arg_i, (list, tuple)) and len(arg_i) == 2 and arg_i[0] == 'pickled_args':
                        d = arg_i[1].data if hasattr(arg_i[1], 'data') else arg_i[1]
                        fn_args = pickle.loads(d)

                    elif isinstance(arg_i, (list, tuple)) and len(arg_i) == 2 and arg_i[0] == 'kwargs':
                        kwargs = arg_i[1]

                    elif isinstance(arg_i, (list, tuple)) and len(arg_i) == 2 and arg_i[0] == 'pickled_kwargs':
                        d = arg_i[1].data if hasattr(arg_i[1], 'data') else arg_i[1]
                        kwargs = pickle.loads(d)

                    else:
                        fn_args.append(arg_i)

                result = fn(*fn_args, **kwargs)

                if not rpcable(result):
                    result = ('pickled_data', Binary(pickle.dumps(result)))

                return result

            except JobQueueEmpty:
                raise JobQueueEmpty

            except Exception as e:
                print('exception raised during execution of function {}:'.format(fn.__name__))
                raise e

        wrapped.__name__ = fn.__name__
        return wrapped

    def _external_security_wrapper(self, fn):

        def wrapped(response_tuple, *args, **kwargs):
            client = self._server.client.address[0] if self._server.client.address is not None else 'local'
            print('handling request for secure function from client: {}'.format(client)) if self.verbosity > 2 else None

            response, salt = response_tuple
            salt = salt.data if hasattr(salt, 'data') else salt

            if client not in self._outstanding_challenges:
                print('challenge was not issued by me') if self.verbosity > 0 else None
                return ChallengeNotValidError

            authorized = False

            with self._threadlocks['server_challenge']:
                for index, (challenge, issue_time) in enumerate(self._outstanding_challenges[client]):
                    test_response = self._generate_response(challenge, salt)[0]
                    if response == test_response:
                        del self._outstanding_challenges[client][index]
                        authorized = True

            if authorized:
                print('accepted response for secure function: {}'.format(fn.__name__)) if self.verbosity > 1 else None
                # print('running secure fn: {}'.format(fn.__name__)) if self.verbosity > 2 else None
                result = fn(*args, **kwargs)
            else:
                print('rejecting response for secure function: {}'.format(fn.__name__)) if self.verbosity > 1 else None
                result = ChallengeNotValidError

            return result

        wrapped.__name__ = fn.__name__
        return wrapped

    def get_completed_jobs(self, flush=False):
        result = [j.unpack() for j in self._completed_jobs.values()]

        if flush:
            self._completed_jobs = {}

        return result

    def rm_completed_job(self, jobid):
        try:
            del self._completed_jobs[jobid]
        except:
            pass
        return

    def do_bookkeeping(self):

        def prune_challenges():
            """
            make sure you have a lock before entering here
            :return:
            """
            if not self._challenge_ttl:
                return

            current_time = time.time()
            purge_ct = 0

            for list in self._outstanding_challenges.values():
                purges = []
                for challenge, issued_time in list:
                    age = current_time - issued_time
                    if age > self._challenge_ttl:
                        purges.append((challenge, issued_time))

                purge_ct += len(purges)

                [list.remove(item) for item in purges]

            print('pruned {} challenges'.format(purge_ct)) if self.verbosity > 1 else None
            # print('outstanding challenges: {}'.format(ages)) if self.verbosity > 1 else None
            # print('tender going to sleep') if self.verbosity > 1 else None

        def prune_jobs():
            """
            make sure you have a lock before entering here
            :return:
            """
            current_time = time.time()

            for job in self._pending_jobs.values():
                if job.timeout is not None:
                    run_time = current_time - job.start_time
                    if run_time > job.timeout:

                        # give up on job and put back in queue
                        print("job {} timed out... putting back on queue.".format(job.id)) if self.verbosity > 0 else None
                        job.start_time = None
                        if job.host is not None or job.host == '':
                            self._job_queues[''].update({job.id: job})
                        else:
                            self._job_queues[job.host].update({job.id: job})
                        del self._pending_jobs[job.id]

        while not self._events['stop_bookkeeper'] and not self._events['shutdown'].is_set():

            with self._threadlocks['server_challenge']:
                prune_challenges()

            with self._threadlocks['jobqueue']:
                prune_jobs()

            self._events['stop_bookkeeper'].wait(timeout=self._bookkeeper_interval)

    def register_remote(self, ip, port=None):
        if ':' in ip and port is None:
            self._remote_ips.append(tuple(ip.split(':')))
        elif ip and not port:
            self._remote_ips.append((ip, self.default_port))
        elif ip and port:
            self._remote_ips.append((ip, port))

    def make_gui(self, ):

        self._tkroot = Tk()
        self._tkroot.title('WaveRunner')

        self._rtvars = {'srv_path': StringVar(),
                       'ip': StringVar(),
                       'iface': StringVar(),
                       'port': StringVar(),
                       'registered_services': StringVar(), }

        self._update_gui_vars()

        note = Notebook(self._tkroot, padding=0)
        note.grid(sticky=N + S + E + W)

        status_tab = Frame(note)
        status_tab.grid(sticky=N + S + E + W)
        config_tab = Frame(note)
        config_tab.grid(sticky=N + S + E + W)

        note.add(status_tab, text="Status", sticky=N + S + E + W, padding=10)
        note.add(config_tab, text="Configure", sticky=N + S + E + W, padding=10)

        """ Status Tab """
        Label(status_tab, text="Waverunner is running", font="Sans 24 bold").grid(columnspan=2)

        ip_lframe = LabelFrame(status_tab, text="Waverunner http server address")
        ip_lframe.grid(row=1, padx=10, pady=10, sticky=E)
        Label(ip_lframe, textvariable=self._rtvars['ip']).grid(row=0, column=0, sticky=E)
        Label(ip_lframe, text=':').grid(row=0, column=1)
        Label(ip_lframe, textvariable=self._rtvars['port']).grid(row=0, column=2, sticky=W)

        testdir_lframe = LabelFrame(status_tab, text="Waverunner tests path")
        testdir_lframe.grid(row=2, padx=10, pady=10, sticky=E)
        Label(testdir_lframe, textvariable=self._rtvars['srv_path']).grid(row=1, column=1)

        password_lframe = LabelFrame(status_tab, text="Password")
        password_lframe.grid(row=3, padx=10, pady=10, sticky=E)
        Label(password_lframe, text=self.password).grid()

        services_lframe = LabelFrame(status_tab, text="Registered Services")
        services_lframe.grid(row=4, padx=10, pady=10, sticky=E)
        Label(services_lframe, textvariable=self._rtvars['registered_services']).grid()

        Button(status_tab, text="Change\nTest Directory", command=self.gui_update_testpath).grid(row=2, column=1,
                                                                                                 sticky=W)
        Button(status_tab, text="Copy", command=self.gui_address_to_clipboard).grid(row=1, column=1, sticky=W)

        Label(status_tab, text='You can get more details by directing a web browser\nto the ip address above.').grid(
            row=5, sticky=S + W)
        Button(status_tab, text="QUIT", bg='red', fg="black", font="sans 24 bold", command=self.exit_gracefully).grid(
            row=5, column=1, sticky=S + E)

        """ Config Tab """
        conff1 = LabelFrame(config_tab, text="select ethernet interface")
        conff1.grid()
        [Radiobutton(conff1, text=str(iface), variable=self._rtvars['iface'], value=str(iface),
                     command=self.resolve_interface_request).grid(column=0, sticky=W) for iface in iflist.keys()]

    def gui_address_to_clipboard(self):
        address = ':'.join([self.ip, str(self.port)])
        self.copytext(address)

    def gui_update_testpath(self):
        cur_path = self.srv_path
        if cur_path:
            newpath = os.path.abspath(tkFileDialog.askdirectory(initialdir=cur_path))
        else:
            newpath = os.path.abspath(tkFileDialog.askdirectory())
        if newpath and os.path.isdir(newpath):
            self.set_testpath(newpath)

    def set_testpath(self, path):
        testpath = os.path.abspath(path)
        if testpath != self.srv_path and testpath != thispath and testpath and testpath is not None:
            serving = bool(self._server)
            _ = self.stop_service() if serving else None
            self.parse_test_dir(testpath)
            _ = self.start_service() if serving else None

    def parse_test_dir(self, new_path):

        testmodules = _list_modules_at_path(new_path)

        print('found modules: {}'.format([item[0] for item in testmodules])) if self.verbosity > 1 else None

        if self.srv_path is not None and self.srv_path in sys.path and self.srv_path != new_path:
            sys.path.remove(self.srv_path)
        self._set_srv_path(new_path)
        if self.srv_path not in sys.path:
            sys.path.append(self.srv_path)

        live_modules = []
        for module_name, module in testmodules:
            try:
                live_modules.append(_get_live_module(module))
            except (ImportError, SyntaxError, TypeError, ValueError) as e:
                if hasattr(e, 'message'):
                    print('problem importing {}: {}. moving on...'.format(module, e.message))
                else:
                    print('problem importing {}: {}. moving on...'.format(module, repr(e)))

        for module in live_modules:
            for itemname, item in [(item, getattr(module, item)) for item in dir(module)]:
                if hasattr(item, '_waverunner_public'):

                    if item._waverunner_public == True:
                        if callable(item):
                            self.register_insecure_method(item, modulename=module.__name__)
                        else:
                            self.register_insecure_instance(item, modulename=module.__name__)

                    elif item._waverunner_public == False:
                        if callable(item):
                            self.register_secure_method(item, modulename=module.__name__)
                        else:
                            self.register_secure_instance(item, modulename=module.__name__)

        if self._srv_methods:
            print('methods available:\n{}'.format('\n'.join(
                ['    {}'.format(name) for name, _ in self._srv_methods]
            )))

        if self._srv_methods_secured:
            print('methods available:\n{}'.format('\n'.join(
                ['    {}'.format(name) for name, _ in self._srv_methods_secured]
            )))

        # if self._srv_instances:
        #     print('instances available:\n{}'.format('\n'.join(
        #         ['    {}'.format(name) for name, _ in self._srv_instances]
        #     )))
        #
        # if self._srv_instances_secured:
        #     print('instances available:\n{}'.format('\n'.join(
        #         ['    {}'.format(name) for name, _ in self._srv_instances_secured]
        #     )))

    def register_secure_method(self, method, modulename=None):
        serving = self._serving
        self.stop_service()
        name = '.'.join([modulename, method.__name__]) if modulename is not None else method.__name__

        secured_method = self._external_security_wrapper(self._external_base_wrapper(method))

        self._secure_method_server._register(name, secured_method)

        self._srv_methods_secured.append((
            name,
            secured_method
        ))

        self._local_methods.append((
            name,
            method,
        ))

        if serving:
            self.start_service()

    def register_insecure_method(self, method, modulename=None):
        assert hasattr(method, '_waverunner_public') and method._waverunner_public == True
        serving = self._serving
        self.stop_service()
        name = '.'.join([modulename, method.__name__]) if modulename is not None else method.__name__

        self._srv_methods.append((
            name,
            self._external_base_wrapper(method)
        ))
        self._local_methods.append((
            name,
            method,
        ))

        if serving:
            self.start_service()

    # def register_secure_instance(self, instance, modulename=None):
    #     serving = self._serving
    #     self.stop_service()
    #     name = '.'.join([modulename, instance.__name__]) if modulename is not None else instance.__name__
    #
    #     self._srv_instances_secured.append((
    #         name,
    #         self._external_security_wrapper(self._external_base_wrapper(instance))
    #     ))
    #     self._local_instances.append((
    #         name,
    #         instance,
    #     ))
    #
    #     if serving:
    #         self.start_service()
    #
    # def register_insecure_instance(self, instance, modulename=None):
    #     assert hasattr(instance, '_waverunner_public') and instance._waverunner_public == True
    #     serving = self._serving
    #     self.stop_service()
    #     name = '.'.join([modulename, instance.__name__]) if modulename is not None else instance.__name__
    #
    #     self._srv_instances.append((
    #         name,
    #         self._external_base_wrapper(instance)
    #     ))
    #     self._local_instances.append((
    #         name,
    #         instance,
    #     ))
    #
    #     if serving:
    #         self.start_service()

    def set_interface(self, ifname):
        ip = iflist[ifname.get()]
        self._set_ip(ip)

    def resolve_interface_request(self, ):
        if self._server is not None:
            needsrestart = True
            self.stop_service()
        else:
            needsrestart = False

        self.set_interface(self._rtvars['iface'])

        if needsrestart:
            self.start_service()

    def copytext(self, text_to_copy=''):
        clip = Tk()
        clip.withdraw()
        clip.clipboard_clear()
        clip.clipboard_append(text_to_copy)
        clip.destroy()

    def start_xmlrpc_server(self, ):

        if self._server_thread is None:

            server = ThreadingRPCServer(addr=(self.ip, int(self.port)),
                                        allow_none=True,
                                        bind_and_activate=False,
                                        logRequests=False)

            # server = RPCServer(addr=(self.ip, int(self.port)),
            #                    allow_none=True,
            #                    bind_and_activate=False,
            #                    logRequests=False)

            server.set_server_title('Waverunner in python')
            server.set_server_documentation('Application provides RPC access to python scripts')
            server.set_server_name('waverunner_' + gethostname())

            # register system functions
            self.register_insecure_method(self.get_challenge)
            self.register_insecure_method(self.notify)
            self.register_insecure_method(self.is_secure)
            self.register_secure_method(self.get_job_list)
            self.register_secure_method(self.get_job)
            self.register_secure_method(self.put_job)

            # for name, fn in self._srv_methods + self._srv_methods_secured:
            for name, fn in self._srv_methods:
                server.register_function(fn, name=name)

            server.register_instance(self._secure_method_server)

            server.register_introspection_functions()
            server.register_multicall_functions()

            def serve_and_die(server):
                server.server_bind()
                server.server_activate()
                server.serve_forever()

            server_thread = threading.Thread(name='xmlrpc_server', target=serve_and_die, args=(server,))
            server_thread.daemon = True
            server_thread.start()

            print('server started at {}:{}'.format(self.ip, self.port))
            self._server = server
            self._server_thread = server_thread
            self._outstanding_challenges.clear()

        else:
            print('server already running... restarting') if self.verbosity > 1 else None
            self.stop_xmlrpc_server()
            self.start_xmlrpc_server()

    def stop_xmlrpc_server(self):
        self._server.shutdown()
        self._server.server_close()
        self._server_thread.join()
        self._server_thread = None
        print('server stopped')

    def start_notify_server(self, ):
        self._events['stop_notify'].clear()
        self._notify_server_thread = threading.Thread(target=self._notify_remotes_forever, name='notifier')
        self._notify_server_thread.daemon = True
        self._notify_server_thread.start()

    def stop_notify_server(self, ):
        self._events['stop_notify'].set()
        self._notify_server_thread.join()

    def start_polling(self):
        self._events['stop_polling'].clear()
        self._poll_remote_hosts_thread = threading.Thread(target=self._poll_remotes_forever, name='remotes_poller')
        self._poll_remote_hosts_thread.daemon = True
        self._poll_remote_hosts_thread.start()

    def stop_polling(self):
        self._events['stop_polling'].set()
        self._poll_remote_hosts_thread.join()

    def start_bookkeeper(self):
        self._events['stop_bookkeeper'].clear()
        self._bookkeeper_thread = threading.Thread(target=self.do_bookkeeping, name='bookkeeper')
        self._bookkeeper_thread.daemon = True
        self._bookkeeper_thread.start()

    def stop_bookkeeper(self):
        self._events['stop_bookkeeper'].set()
        self._bookkeeper_thread.join()

    def start_service(self, ):
        if not self._serving:
            self.start_xmlrpc_server()
            self.start_bookkeeper()
            self.start_notify_server()
            self.start_polling()
            self._serving = True

    def stop_service(self, ):
        if self._serving:
            self.stop_xmlrpc_server()
            self.stop_bookkeeper()
            self.stop_notify_server()
            self.stop_polling()
            self._serving = False

    def serve_forever(self):
        self.start_service()
        try:
            while not self._events['shutdown'].is_set():
                self._events['shutdown'].wait(1)
        except:
            pass
        finally:
            self.exit_gracefully()

    def join(self):
        try:
            while not self._events['shutdown'].is_set():
                self._events['shutdown'].wait(1)
        except:
            pass
        finally:
            self.exit_gracefully()

    def exit_gracefully(self, ):
        self._events['shutdown'].set()
        self.stop_service()
        if self._tkroot is not None:
            self._tkroot.quit()
            self._tkroot = None

        if self._worker_pool:
            try:
                self._worker_pool.shutdown()
            except:
                pass

    def list_remote_services(self):
        return repr(self.registered_services)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--directory', '-d', default=None)
    parser.add_argument('--port', '-p', type=int, default=default_port)
    parser.add_argument('--remotes', '-r', default=default_remote_ips)
    parser.add_argument('--password', '-s', default=default_password)
    parser.add_argument('--notify-interval', '-i', nargs='?', type=int, default=0, const=default_notify_interval)
    parser.add_argument('--poll-interval', '-I', nargs='?', type=int, default=0, const=default_poll_interval)
    parser.add_argument('--gui', action='store_true')
    parser.add_argument('--verbosity', '-v', type=int, default=1)
    parser.add_argument('--n-workers', '-n', type=int, default=default_max_n_workers)

    args = parser.parse_args()

    if args.directory:
        if not os.path.isdir(args.directory):
            print("invalid directory specified")
            sys.exit(1)
        else:
            args.directory = os.path.abspath(args.directory)

    if not 10 < int(args.port) < 65535:
        print('invalid port specified')
        sys.exit(1)

    server = Waverunner(
        port=args.port,
        remote_ips=args.remotes,
        path_to_serve=args.directory,
        password=args.password,
        notify_interval=args.notify_interval,
        polling_interval=args.poll_interval,
        verbosity=args.verbosity,
        max_n_workers=args.n_workers,
    )

    try:
        if args.gui:
            server.make_gui()
            server.start_service()
            server._tkroot.mainloop()

        if not __name__ == '__main__':
            return server

        else:
            server.serve_forever()

    finally:
        server.exit_gracefully()


if __name__ == '__main__':
    main()
