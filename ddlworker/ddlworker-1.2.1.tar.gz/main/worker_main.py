import os, os.path
import argparse
import sys
import shutil
import multiprocessing as mp
from time import sleep

# Add the top-level directory to the PYTHONPATH
worker_main_dir_path = os.path.dirname(os.path.realpath(__file__))
worker_dir_path = os.path.abspath(os.path.join(worker_main_dir_path, os.pardir))
sys.path.insert(0, worker_dir_path)

from main.worker_entry import worker_entry
from main.utils import register, registered, load_worker_runtime, get_registered_workers, gpu_uuid_to_gpu_id
from main.utils import RUNTIME_MASTER_SERVER_KEY

###############################################################################

def workers_start(runtime, metadir, workdir):
    registered_workers = get_registered_workers(metadir)
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
                             metadir,
                             worker_config["port"],
                             worker_uuid,
                             worker_config["gpu_id"]))

        worker_processes[worker_uuid] = {
            'process' : p,
            'config' : worker_config
        }

        p.start()

    if not worker_processes:
        return

    # If a worker is stopped, restart it.
    while True:
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
                                 metadir,
                                 worker_config["port"],
                                 worker_uuid,
                                 worker_config["gpu_id"]))

            worker_context['process'] = p
            p.start()

        sleep(300)

    return

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--workdir',
        type=str,
        required=True,
        help='work directory for the worker, must be an absolute path')
    parser.add_argument(
        '--metadir',
        type=str,
        required=True,
        help='meta directory for the worker, must be an absolute path')
    parser.add_argument(
        '-d',
        '--debug',
        action='store_true',
        help='debug mode')
    parser.add_argument(
        '--secrete',
        type=str,
        default=None,
        help='secrete')
    FLAGS, _ = parser.parse_known_args()
    debug_mode = FLAGS.debug
    workdir = FLAGS.workdir
    metadir = FLAGS.metadir
    secrete = FLAGS.secrete

    # If meta folder does not exist, exit now.
    if not os.path.isdir(metadir):
        print("[Error::FATAL] Does not have a valid meta folder.")
        return

    # If workdir does not exist, exit now.
    if not os.path.isdir(workdir):
        print("[Error::FATAL] Does not have a valid workdir.")
        return

    # Load runtime configuration based on whehter in debug mode or not.
    runtime = load_worker_runtime(debug_mode)

    # Check if worker has already been registered.
    if not registered(metadir):
        success = register(runtime, metadir, workdir, secrete)
        # Registration failure is fatal. Exit now.
        if not success:
            return

    workers_start(runtime, metadir, workdir)
    return

if __name__ == '__main__':
    main()