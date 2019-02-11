#!/usr/bin/env python
import atexit
import json
import logging
import os
import platform
import shlex
import signal
import subprocess
import threading
import time

import paramiko

from spell.cli.jupyter.spell_kernel.logger import SpellKernelLogger


class SSHKernelException(Exception):
    pass


class CommandNotFound(SSHKernelException):
    def __init__(self, command=None):
        msg = "command not found"
        if command is not None:
            msg += ": {}".format(command)
        super(CommandNotFound, self).__init__(msg)


class SSHConn:
    CONNECT_FIELDS = [
        "hostname",
        "port",
        "username",
        "key_filename",
    ]

    def __init__(self, ssh_config, prompt="~$"):
        self.ssh_config = {
            k: v for k, v in ssh_config.items()
            if k in self.CONNECT_FIELDS
        }
        self.prompt = prompt

        self._client = paramiko.SSHClient()
        self._client.load_system_host_keys()
        # TODO(peter): Use RejectPolicy
        self._client.set_missing_host_key_policy(paramiko.AutoAddPolicy)

        self._channel = None

    def connect(self, env=None):
        self._client.connect(**self.ssh_config)
        # Set ServerAliveInterval to 30s
        self._client.get_transport().set_keepalive(30)
        self._channel = self._client.invoke_shell()
        self.recv_until(self.prompt)

    def sendline(self, line):
        if self._channel is None:
            raise SSHKernelException("Sending data: Channel does not exist")

        data = line + "\n"
        self._channel.sendall(data)

    def run_command(self, command):
        self.sendline(command)
        return self.recv_until(self.prompt)

    def recv_until(self, output):
        if self._channel is None:
            raise SSHKernelException("Waiting for prompt: Channel does not exist")

        data = self._channel.recv(4096).decode("utf-8")
        window = data
        while output not in window:
            window = window.split("\n")[-1]

            new = self._channel.recv(4096).decode("utf-8")
            window += new
            data += new
        return data


class SSHKernel:
    def __init__(self, host, ssh_config, connection_info, conda_env, workdir, verbose=False):
        self.host = host
        self.ssh_config = ssh_config
        self.ssh_command = self._build_ssh_command(ssh_config)
        self.connection_info = connection_info
        self.conda_env = conda_env
        self.workdir = workdir

        log_level = logging.DEBUG if verbose else logging.INFO
        self.logger = SpellKernelLogger("SpellKernel", level=log_level)

        self._kernel_conn = None
        self._interrupt_conn = None

        self._kernel_pid = None
        self._tunnel_proc = None
        self._running = True

    def connect_ssh(self):
        if not self._running:
            return

        self.logger.debug("Connecting via SSH")

        exception = [None]

        def get_kernel_conn():
            if self._kernel_conn is None:
                for i in range(10):
                    try:
                        self._kernel_conn = self._open_ssh_conn()
                        return
                    except SSHKernelException as e:
                        exception[0] = e
                        time.sleep(1)
                    except Exception as e:
                        exception[0] = e
                self._kernel_conn = None

        def get_interrupt_conn():
            if self._interrupt_conn is None:
                for i in range(10):
                    try:
                        self._interrupt_conn = self._open_ssh_conn()
                        return
                    except SSHKernelException as e:
                        exception[0] = e
                        time.sleep(1)
                    except Exception as e:
                        exception[0] = e
                self._interrupt_conn = None

        kernel_thread = threading.Thread(target=get_kernel_conn)
        kernel_thread.start()
        interrupt_thread = threading.Thread(target=get_interrupt_conn)
        interrupt_thread.start()

        kernel_thread.join()
        interrupt_thread.join()

        # If the connection didn't work, raise an exception in the main thread
        if self._kernel_conn is None or self._interrupt_conn is None:
            if exception[0] is not None:
                raise exception[0]
            raise SSHKernelException("connection failed")

    def initialize_remote(self):
        if not self._running:
            return

        if self.conda_env is not None:
            self._kernel_conn.run_command(". activate '{}'".format(self.conda_env))

        marshalled = json.dumps(self.connection_info)
        cmd = "(cd {} && sudo env \"PATH=$PATH\" \"SPELL_RUN=true\" spell-kernel '{}')".format(self.workdir, marshalled)
        kernel_output = self._kernel_conn.run_command(cmd)

        cmd_output = kernel_output.split('\r\n')[-2]
        if cmd_output.endswith("No such file or directory"):
            raise CommandNotFound("spell-kernel")

        self._kernel_pid = int(cmd_output)
        self.logger.debug("Successfully started kernel, pid is {}".format(self._kernel_pid))

    def tunnel_ports(self):
        if not self._running:
            return

        port_forwards = " ".join(
            "-L 127.0.0.1:{port}:127.0.0.1:{port}".format(port=port)
            for key, port in self.connection_info.items()
            if key.endswith("_port")
        )
        ssh_cmd = "{ssh_cmd} -N {port_forwards} {host}".format(
            ssh_cmd=self.ssh_command,
            port_forwards=port_forwards,
            host=self.host,
        )

        def catch_sigint():
            signal.signal(signal.SIGINT, signal.SIG_IGN)

        self.logger.debug("Tunneling ports")
        try:
            devnull = open(os.devnull, 'w')
            tunnel_proc = subprocess.Popen(shlex.split(ssh_cmd, posix=platform.system() != "Windows"),
                                           preexec_fn=catch_sigint if platform.system() != "Windows" else None,
                                           stdout=devnull, stderr=devnull)
        except Exception as e:
            raise SSHKernelException("could not tunnel ports: {}".format(str(e)))

        def cleanup_tunnels():
            try:
                tunnel_proc.terminate()
            except OSError:
                pass
        atexit.register(cleanup_tunnels)

        self._tunnel_proc = tunnel_proc
        pid = self._tunnel_proc.pid
        self.logger.debug("Successfully tunnelled ports, pid is {}".format(pid))

    def health_check(self):
        cmd = "spell-check '{}'".format(self._kernel_pid)
        kernel_output = self._kernel_conn.run_command(cmd)

        cmd_output = kernel_output.split('\r\n')[-2]
        if cmd_output.endswith("command not found"):
            raise CommandNotFound("spell-check")

        ecode = int(cmd_output)
        return ecode == 0

    def keep_alive(self):
        if not self._running:
            return

        while self._running:
            try:
                if not self.health_check():
                    self.logger.debug("Kernel process died")
                    self.initialize_remote()

                if self._tunnel_proc.poll() is not None:
                    self.logger.debug("Tunnels died")
                    self.tunnel_ports()
            finally:
                time.sleep(0.5)

        self.logger.info("Kernel has died")

    def interrupt(self):
        if self._kernel_pid is None:
            return

        cmd = "sudo kill -2 '{}'".format(self._kernel_pid)
        self._interrupt_conn.run_command(cmd)
        self.logger.debug("Successfully interrupted kernel")

    def _open_ssh_conn(self):
        env = os.environ.copy()
        env["TERM"] = "xterm-old"
        ssh_conn = SSHConn(self.ssh_config)
        ssh_conn.connect(env=env)
        return ssh_conn

    def _build_ssh_command(self, ssh_config):
        cmd = "ssh -p {port} -l {username}".format(**ssh_config)
        for key_path in ssh_config.get("key_filename", []):
            cmd += " -i {path}".format(path=key_path)
        for opt in ssh_config.get("options", []):
            cmd += " -o {opt}".format(opt=opt)
        return cmd
