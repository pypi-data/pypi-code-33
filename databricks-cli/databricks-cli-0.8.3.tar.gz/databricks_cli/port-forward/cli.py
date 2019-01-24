# Databricks CLI
# Copyright 2017 Databricks, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License"), except
# that the use of services to which certain application programming
# interfaces (each, an "API") connect requires that the user first obtain
# a license for the use of the APIs from Databricks, Inc. ("Databricks"),
# by creating an account at www.databricks.com and agreeing to either (a)
# the Community Edition Terms of Service, (b) the Databricks Terms of
# Service, or (c) another written agreement between Licensee and Databricks
# for the use of the APIs.
#
# You may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import atexit
import click
import json
import os
import struct
import termios
from select import select
import sys
import time
import tty
import traceback
import websocket

try:
    from shutil import get_terminal_size
except ImportError:
    from backports.shutil_get_terminal_size import get_terminal_size

try:
    import thread
except ImportError:
    import _thread as thread

from databricks_cli.configure.config import provide_api_client, profile_option
from databricks_cli.utils import eat_exceptions, CONTEXT_SETTINGS
from databricks_cli.ssh_utils import launch_websocket_blocking, send_control_message


STREAM_INDICATOR_CONNECTED = 1
STREAM_INDICATOR_OUTPUT = 2
STREAM_INDICATOR_ERROR = 3
STREAM_INDICATOR_STATUS = 4

INPUT_INDICATOR_STDIN = 1
INPUT_INDICATOR_TERMSIZE = 2

exit_code = None
local_remote_port_mapping = None
last_termsize = None

def on_connect(ws):
    remote_port = local_remote_port_mapping[1]
    local_port = local_remote_port_mapping[0]
    commandJson = json.dumps({"portForward": { "host" : "127.0.0.1", "port": remote_port}})
    ws.send(commandJson)
    sys.stderr.write("Connection established. Local port = %s, remote port = %s" % (local_port, remote_port))
    sys.stderr.flush()
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("127.0.0.1", local_remote_port_mapping[0]))
    s.listen(1)
    conn, addr = s.accept()
    thread.start_new_thread(pipe_from_socket, (ws, conn))

def on_message(ws, message_type, message_bytes):
    if message_type == STREAM_INDICATOR_CONNECTED:
        on_connect(ws)
    elif message_type == STREAM_INDICATOR_OUTPUT:
        sys.stdout.write(message_bytes)
        sys.stdout.flush()
    elif message_type == STREAM_INDICATOR_STATUS:
        pass
    else:
        raise Error("Unknown stream indicator: %s" % stream_indicator)

def pipe_from_socket(ws, conn):
    try:
        while True:
            data = conn.recv(BUFFER_SIZE)
            if not data:
                ws.close()
                return
            send_control_message(ws, INPUT_INDICATOR_STDIN, data)
    except Exception, err:
        traceback.print_exc()


@click.command(context_settings=CONTEXT_SETTINGS)
@click.argument("cluster-id")
@click.argument("port_mapping")
@profile_option
@eat_exceptions
@provide_api_client
def port_forward_cmd(api_client, cluster_id, port_mapping):
    """
    Creates a job.

    The specification for the json option can be found
    https://docs.databricks.com/api/latest/jobs.html#create
    """
    global exit_code, local_remote_port_mapping

    local_remote_port = port_mapping.split(":", 1)
    if len(local_remote_port) == 2:
        local_remote_port_mapping = (int(local_remote_port[0]), int(local_remote_port[0]))
    else:
        local_remote_port_mapping = (int(port_mapping), int(port_mapping))
    launch_websocket_blocking(api_client, cluster_id, on_message)
