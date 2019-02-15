import os, os.path
import argparse
import sys
import multiprocessing as mp
from time import sleep

# Add the top-level directory to the PYTHONPATH
worker_main_dir_path = os.path.dirname(os.path.realpath(__file__))
worker_dir_path = os.path.abspath(os.path.join(worker_main_dir_path, os.pardir))
sys.path.insert(0, worker_dir_path)

from main.worker_entry import worker_entry
from main.utils import register, \
                       registered, \
                       load_worker_runtime, \
                       get_registered_workers, \
                       gpu_uuid_to_gpu_id

from main.utils import DDL_DEFAULT_LOG_FOLDER_NAME

###############################################################################

DDL_WORKDIR_NAME = "workdir"
DDL_METADIR_NAME = "meta"
DDL_LOGDIR_NAME = "log"
DDL_DATADIR_NAME = "data"

###############################################################################

def workers_start(runtime, datadir):
    registered_workers = get_registered_workers()
    if not registered_workers:
        print("[Error::FATAL] Malformed worker register file or no worker.")
        return

    worker_processes = {}
    for worker_uuid in registered_workers.keys():
        worker_config = registered_workers[worker_uuid]
        success, gpu_id = gpu_uuid_to_gpu_id(runtime, worker_config["gpu_uuid"])
        if not success:
            print("[Error::FATAL] Worker {} has an invalid GPU {}. Skip it.".format(
                  worker_uuid,
                  worker_config["gpu_uuid"]))

            continue

        worker_config["gpu_id"] = gpu_id
        p = mp.Process(target=worker_entry,
                       args=(runtime,
                             worker_config["workdir"],
                             worker_config["logdir"],
                             worker_config["port"],
                             worker_uuid,
                             worker_config["gpu_id"]))

        worker_processes[worker_uuid] = {
            'process': p,
            'config': worker_config
        }

        p.start()

    if not worker_processes:
        return

    # Monitor the health of all the processes.
    while True:
        # Make sure the workers are running.
        for worker_uuid in worker_processes.keys():
            worker_context = worker_processes[worker_uuid]
            process = worker_context['process']
            if process.is_alive():
                continue

            process.join()
            worker_config = worker_context['config']
            p = mp.Process(target=worker_entry,
                           args=(runtime,
                                 worker_config["workdir"],
                                 worker_config["logdir"],
                                 worker_config["port"],
                                 worker_uuid,
                                 worker_config["gpu_id"]))

            worker_context['process'] = p
            p.start()

        sleep(300)

    return


def main(debug_config=None):
    if debug_config is None:
        parser = argparse.ArgumentParser()
        parser.add_argument(
            '--appdir',
            type=str,
            required=True,
            help='app directory for the DDL worker, must be an absolute path')
        parser.add_argument(
            '-d',
            '--debug',
            action='store_true',
            help='debug mode')
        parser.add_argument(
            '-c',
            '--cpu',
            action='store_true',
            help='use CPU instead of GPU (only applicable if -d flag is set)')
        parser.add_argument(
            '--secrete',
            type=str,
            default=None,
            help='secrete')
        FLAGS, _ = parser.parse_known_args()
        debug_mode = FLAGS.debug
        if not debug_mode:
            cpu_mode = False
        else:
            cpu_mode = FLAGS.cpu

        appdir = FLAGS.appdir
        secrete = FLAGS.secrete
    else:
        debug_mode = debug_config.get('debug_mode', False)
        cpu_mode = debug_config.get('cpu_mode', False)
        secrete = debug_config.get('secrete', None)
        appdir = debug_config['appdir']

    workdir = os.path.join(appdir, DDL_WORKDIR_NAME)
    metadir = os.path.join(appdir, DDL_METADIR_NAME)
    logdir = os.path.join(appdir, DDL_LOGDIR_NAME)
    datadir = os.path.join(appdir, DDL_DATADIR_NAME)

    # If app folder does not exist, exit now.
    if not os.path.isdir(appdir):
        print("[Error::FATAL] Does not have a valid app folder.")
        return

    # If metadir does not exist, exit now.
    if not os.path.isdir(metadir):
        print("[Error::FATAL] Does not have a valid metadir.")
        return

    # If workdir does not exist, create one.
    if not os.path.isdir(workdir):
        os.mkdir(workdir)

    # If datadir does not exist, create one.
    if not os.path.isdir(datadir):
        os.mkdir(datadir)

    # If logdir does not exist, create one.
    if not os.path.isdir(logdir):
        os.mkdir(logdir)

    default_log_dir = os.path.join(logdir, DDL_DEFAULT_LOG_FOLDER_NAME)
    if not os.path.isdir(default_log_dir):
        os.mkdir(default_log_dir)

    # Load runtime configuration based on whehter in debug mode or not.
    runtime = load_worker_runtime(debug_mode, cpu_mode)

    # Check if worker has already been registered.
    success, worker_registerd = registered()
    if not success:
        # If the db cannot be connected, it is fatal. Exit now.
        return

    if not worker_registerd:
        success = register(runtime, metadir, workdir, logdir, secrete)
        # Registration failure is fatal. Exit now.
        if not success:
            return

    workers_start(runtime, datadir)
    return


if __name__ == '__main__':
    main()
