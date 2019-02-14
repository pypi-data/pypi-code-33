#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse
import copy
import json
import logging
import os
import posixpath
import queue
import signal
import threading
import traceback

from jupyter_client.session import Session
import zmq
from zmq.eventloop import ioloop, zmqstream

from spell.api import runs_client
from spell.cli.jupyter.spell_kernel.logger import SpellKernelLogger
from spell.cli.jupyter.spell_kernel.sshkernel import SSHKernel
from spell.cli.utils.sentry import capture_exception


KERNEL_PROTOCOL_VERSION = "5.1"
SPELL_KERNEL_VERSION = "0.1.0"


class SpellKernelException(Exception):
    pass


class SpellKernel(object):
    _kernel_info = {
        "protocol_version": KERNEL_PROTOCOL_VERSION,
        "implementation": "spell_kernel",
        "implementation_version": SPELL_KERNEL_VERSION,
        "banner": "Spell kernel (v{})".format(SPELL_KERNEL_VERSION),
        "language_info": {
            "mimetype": "text/x-python",
            "nbconvert_exporter": "python",
            "name": "python",
            # TODO(peter): Make Python version configurable
            "pygments_lexer": "ipython2",
            "version": "3.6.4",
            "file_extension": ".py",
            "codemirror_mode": "python"
        },
        # TODO(peter): Include help_links to Spell docs
    }

    def __init__(self, run_id, conda_env, local_root, remote_root, ssh_host, ssh_port, api_opts, kernel_spec, owner,
                 keys=None, verbose=False):
        self.run_id = run_id
        self.conda_env = conda_env
        self.ssh_host = ssh_host
        self.ssh_port = ssh_port
        self.api_opts = api_opts
        self.kernel_spec = kernel_spec
        self.owner = owner
        self.keys = [] if keys is None else keys

        if local_root is not None and remote_root is not None:
            # Get the relative path to the notebook file on the remote
            local_relpath = os.path.relpath(os.getcwd(), local_root)
            path_pieces = local_relpath.split(os.sep)
            self.remote_workdir = posixpath.join(remote_root, *path_pieces)
        elif local_root is None and remote_root is None:
            self.remote_workdir = ""
        else:
            self.logger.info("Local root and remote root not both provided")

        self.verbose = verbose
        log_level = logging.DEBUG if self.verbose else logging.INFO
        self.logger = SpellKernelLogger("SpellKernel", level=log_level)
        self.serializer = Session(
            username=self.owner,
            signature_scheme=self.kernel_spec["signature_scheme"],
            key=self.kernel_spec.get("key", "").encode("utf-8"),
        )
        self.ioloop = ioloop.IOLoop.instance()
        self.run_status_queue = queue.Queue()
        self.ssh_kernel = None

        self._running = True
        self._sent_start_message = False
        self._waiting_cell = None
        self._message_queue = queue.Queue()

    def initial_setup(self):
        self.logger.debug("Starting initial setup")
        # Set up the local sockets we need to do the initial handshake
        zmq_ctx = zmq.Context()
        self.local_streams = self._init_local_sockets(zmq_ctx)

        # Register callback for the initial kernel_info handshake
        self.local_streams["shell"].on_recv(self.handle_startup_shell)
        self.local_streams["control"].on_recv(self.handle_startup_control)

        # Handle interrupts
        signal.signal(signal.SIGINT, self.handle_startup_signals)

        # Start listening
        ioloop_thread = threading.Thread(target=self.ioloop.start)
        ioloop_thread.start()
        self.logger.debug("Listening for connections")

        # Set up the sockets we'll need for the SSH kernel
        self.dummy_sockets, self.remote_ports = self._init_dummy_sockets(zmq_ctx)
        self.recv_streams = self._init_recv_sockets(zmq_ctx)

        # Start tracking the run status
        run_status_thread = threading.Thread(target=self.track_run_status)
        run_status_thread.start()

        # Build the SSH kernel
        ssh_config = self._build_ssh_config()
        connection_info = self._build_ssh_connection_info()
        self.ssh_kernel = SSHKernel(
            host=self.ssh_host,
            ssh_config=ssh_config,
            connection_info=connection_info,
            conda_env=self.conda_env,
            workdir=self.remote_workdir,
            verbose=self.verbose,
        )

    def ssh_setup(self):
        self.logger.debug("Instantiating remote kernel")

        # Start the kernel on the remote
        try:
            self.ssh_kernel.connect_ssh()
        except Exception:
            self.handle_startup_exception()
            return
        self.logger.debug("SSH connected")

        try:
            self.ssh_kernel.initialize_remote()
        except Exception:
            self.handle_startup_exception()
            return
        self.logger.debug("Remote kernel ready")

        # Close the sockets that were reserving ports
        for socket in self.dummy_sockets.values():
            socket.close()
        # Set up the tunnels
        try:
            self.ssh_kernel.tunnel_ports()
        except Exception:
            self.handle_startup_exception()
            return
        self.logger.debug("Tunnels ready")

        # Stop the callbacks that were used for initialization
        self.local_streams["shell"].stop_on_recv()
        # Stitch the sockets receiving from client to those sending to remote
        self.stitch_sockets(self.local_streams, self.recv_streams)

        # Purge the message queue
        while not self._message_queue.empty():
            raw_msg = self._message_queue.get()
            self.recv_streams["shell"].send_multipart(raw_msg)

        # Set kernel status to ready
        content = {
            "execution_state": "idle",
        }
        self._send("iopub", "status", content)

        # Keep the kernel alive
        signal.signal(signal.SIGINT, self.handle_signals)
        try:
            self.ssh_kernel.keep_alive()
        except Exception as e:
            self.logger.critical("Kernel has died: {}".format(e))

    def handle_startup_shell(self, msg_list):
        idents, msg = self._deserialize(msg_list)
        msg_type = msg["header"]["msg_type"]

        if msg_type == "kernel_info_request":
            if not self._sent_start_message:
                state = "starting"
                self._sent_start_message = True
            else:
                state = "idle"

            content = {
                "execution_state": state,
            }
            self._send("iopub", "status", content, parent=msg, ident=idents)
            self._send("shell", "kernel_info_reply", self._kernel_info, parent=msg, ident=idents)

        elif msg_type == "execute_request":
            # TODO(peter): Publish execute_input messages on iopub too
            self._message_queue.put(msg_list)

        elif msg_type == "shutdown_request":
            self.handle_shutdown(idents, msg)

    def handle_startup_control(self, msg_list):
        idents, msg = self._deserialize(msg_list)
        msg_type = msg["header"]["msg_type"]

        if msg_type == "shutdown_request":
            self.handle_shutdown(idents, msg)

    def handle_startup_signals(self, signum, frame):
        if signum == 2:
            if self._waiting_cell is not None:
                content = {
                    "status": "error",
                }
                self._send("shell", "execute_reply", content,
                           parent=self._waiting_cell["parent"],
                           ident=self._waiting_cell["ident"])
                self._waiting_cell = None

    def handle_startup_exception(self):
        self.logger.critical("Exception raised")
        self.logger.critical(traceback.format_exc())
        self._running = False

    def handle_shutdown(self, idents, msg):
        # Stop the SSH kernel
        if self.ssh_kernel is not None:
            self.ssh_kernel._running = False

        # Reply to the restart request
        restart = msg["content"]["restart"]
        content = {
            "restart": restart,
        }
        self._send("shell", "shutdown_reply", content, parent=msg, ident=idents)
        self.logger.debug("Sent shutdown reply")

        # Stop the tornado ioloop
        self.ioloop.stop()

    def handle_signals(self, signum, frame):
        if signum == 2:
            self.ssh_kernel.interrupt()

    def stitch_sockets(self, local_streams, recv_streams):
        for name in local_streams.keys():
            local_stream = local_streams[name]
            recv_stream = recv_streams[name]

            local_stream.on_recv(self.stitch_to(recv_stream, name, "local"))
            recv_stream.on_recv(self.stitch_to(local_stream, name, "recv"))

    def stitch_to(self, dest, name, src):
        if name == "iopub" or name == "stdin":
            def send_msg(raw_msg):
                dest.send_multipart(raw_msg)
        elif name == "shell" or name == "control":
            def send_msg(raw_msg):
                idents, msg = self._deserialize(raw_msg)
                if msg["header"]["msg_type"] == "shutdown_request":
                    self.logger.debug("got a shutdown request")
                    self.handle_shutdown(idents, msg)
                dest.send_multipart(raw_msg)
        elif name == "hb":
            def send_msg(raw_msg):
                # TODO(peter): Implement this
                self.handle_hb(raw_msg)
        return send_msg

    def track_run_status(self):
        try:
            r_client = runs_client.RunsClient(owner=self.owner, **self.api_opts)
            for entry in r_client.get_run_log_entries(str(self.run_id), follow=True, offset=0):
                if entry.status_event:
                    self.run_status_queue.put(entry.status)

            self._running = False
            if self.ssh_kernel is not None:
                self.ssh_kernel._running = False
        except Exception:
            self.handle_startup_exception()

    def wait_for_run(self):
        break_statuses = set(["running", "killing", "stopping", "failed"])
        while self._running:
            status = self.run_status_queue.get()
            if status in break_statuses:
                break
        self.logger.debug("Run is ready")

    def _send(self, stream, msg_type, content, parent=None, ident=None, flush=False):
        self.serializer.send(
            stream=self.local_streams[stream],
            msg_or_type=msg_type,
            parent=parent,
            ident=ident,
            content=content
        )
        if flush:
            self.local_streams[stream].flush()

    def _deserialize(self, raw_msg):
        idents, msg_list = self.serializer.feed_identities(raw_msg)
        msg = self.serializer.deserialize(msg_list)
        return idents, msg

    def _init_local_sockets(self, ctx):
        """ Set up the sockets that will be speaking directly to Jupyter """
        sockets = {
            "hb": ctx.socket(zmq.REP),
            "iopub": ctx.socket(zmq.PUB),
            "control": ctx.socket(zmq.ROUTER),
            "stdin": ctx.socket(zmq.ROUTER),
            "shell": ctx.socket(zmq.ROUTER),
        }
        for name, sock in sockets.items():
            transport = self.kernel_spec["transport"]
            ip = self.kernel_spec["ip"]
            port = self.kernel_spec["{}_port".format(name)]
            sock.bind("{}://{}:{}".format(transport, ip, port))

        streams = {
            name: zmqstream.ZMQStream(sock, self.ioloop)
            for name, sock in sockets.items()
        }
        return streams

    def _init_recv_sockets(self, ctx):
        """ Set up the sockets that will be speaking with the remote """
        sockets = {
            "hb": ctx.socket(zmq.REQ),
            "iopub": ctx.socket(zmq.SUB),
            "control": ctx.socket(zmq.DEALER),
            "stdin": ctx.socket(zmq.DEALER),
            "shell": ctx.socket(zmq.DEALER),
        }
        for name, sock in sockets.items():
            transport = self.kernel_spec["transport"]
            ip = self.kernel_spec["ip"]
            port = self.remote_ports[name]
            sock.connect("{}://{}:{}".format(transport, ip, port))
            if name == "iopub":
                # Subscribe iopub socket to all messages
                sock.setsockopt(zmq.SUBSCRIBE, b'')

        streams = {
            name: zmqstream.ZMQStream(sock, self.ioloop)
            for name, sock in sockets.items()
        }
        return streams

    def _init_dummy_sockets(self, ctx):
        """ Reserve local sockets so we don't disturb anything running locally when we forward traffic """
        sockets = {
            "hb": ctx.socket(zmq.REP),
            "iopub": ctx.socket(zmq.PUB),
            "control": ctx.socket(zmq.ROUTER),
            "stdin": ctx.socket(zmq.ROUTER),
            "shell": ctx.socket(zmq.ROUTER),
        }
        ports = {}
        for name, sock in sockets.items():
            transport = self.kernel_spec["transport"]
            ip = self.kernel_spec["ip"]
            port = sock.bind_to_random_port("{}://{}".format(transport, ip))
            ports[name] = port
        return sockets, ports

    def _build_ssh_config(self):
        ssh_config = {
            "hostname": self.ssh_host,
            "port": self.ssh_port,
            "username": "{}#{}".format(self.owner, self.run_id),
            "key_filename": self.keys,
            "options": [
                "ServerAliveInterval=30",
                # TODO(peter): Use StrictHostKeyChecking
                "StrictHostKeyChecking=no",
            ],
        }
        return ssh_config

    def _build_ssh_connection_info(self):
        connection_info = copy.deepcopy(self.kernel_spec)
        for name, port in self.remote_ports.items():
            key = "{}_port".format(name)
            connection_info[key] = port
        return connection_info


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--owner", required=True)
    parser.add_argument("--ssh-host", help=argparse.SUPPRESS,
                        default="ssh.spell.run")
    parser.add_argument("--ssh-port", help=argparse.SUPPRESS,
                        default=22, type=int)
    parser.add_argument("--api-url", help=argparse.SUPPRESS,
                        default="https://api.spell.run")
    parser.add_argument("--api-version", help=argparse.SUPPRESS,
                        default="v1")
    parser.add_argument("--api-token", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--key", action="append", default=[])
    parser.add_argument("--conda-env")
    parser.add_argument("--local-root")
    parser.add_argument("--remote-root")
    parser.add_argument("--verbose", action="store_true")
    parser.add_argument("connection_file")

    return parser.parse_args()


def main():
    args = parse_args()

    with open(args.connection_file) as cf:
        kernel_spec = json.load(cf)

    api_opts = {
        "token": args.api_token,
        "base_url": args.api_url,
        "version_str": args.api_version,
    }

    sk = SpellKernel(args.run_id,
                     args.conda_env,
                     args.local_root,
                     args.remote_root,
                     args.ssh_host,
                     args.ssh_port,
                     api_opts,
                     kernel_spec,
                     owner=args.owner,
                     keys=args.key,
                     verbose=args.verbose)
    sk.initial_setup()
    # TODO(peter): Clean this up
    if not sk._running:
        return
    sk.wait_for_run()
    if not sk._running:
        return
    sk.ssh_setup()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        capture_exception(e)
        raise
