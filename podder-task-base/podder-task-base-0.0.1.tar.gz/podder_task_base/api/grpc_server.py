import os
import time
from concurrent import futures

import daemon
import grpc
from daemon import pidfile

import pipeline_framework_pb2_grpc
from podder_task_base.api.task_api import PocBaseApi

_ONE_DAY_IN_SECONDS = 60 * 60 * 24
DEFAULT_MAX_WORKERS = 10
DEFAULT_PORT = 50051
GRPC_PID_FILE = os.environ.get("GRPC_PID_FILE")


def serve():
    max_workers = os.environ.get("GRPC_MAX_WORKERS") if os.environ.get(
        "GRPC_MAX_WORKERS") else DEFAULT_MAX_WORKERS
    port = os.environ.get("GRPC_PORT") if os.environ.get(
        "GRPC_PORT") else DEFAULT_PORT

    server = grpc.server(
        futures.ThreadPoolExecutor(max_workers=int(max_workers)))
    pipeline_framework_pb2_grpc.add_PocBaseApiServicer_to_server(
        PocBaseApi(), server)
    server.add_insecure_port('[::]:' + str(port))

    server.start()
    print("[{}] gRPC server is listening to port: '[::]:{}'".format(
        time.strftime("%Y-%m-%d %H:%m:%S"), port))
    try:
        while True:
            time.sleep(_ONE_DAY_IN_SECONDS)
    except KeyboardInterrupt:
        server.stop(0)


if __name__ == '__main__':
    stdout = open(os.environ.get("GRPC_LOG"), 'a')
    stderr = open(os.environ.get("GRPC_ERROR_LOG"), 'a')
    pidfile = daemon.pidfile.PIDLockFile(GRPC_PID_FILE)
    with daemon.DaemonContext(
            stdout=stdout, stderr=stderr, pidfile=pidfile,
            detach_process=True):
        serve()
