import errno
import os.path
import socket, errno
import uuid
import yaml

from worker.worker_start import *

from io.dbinterface import *

###############################################################################

RUNTIME_MASTER_SERVER_KEY = "MASTER_SERVER"
RUNTIME_GPU_UUID_TO_ID_KEY = "GPU_UUID_TO_ID"
RUNTIME_CPU_MODE_KEY = "CPU_MODE"

GPU_REGISTER_FILE_NAME = "gpu_register.yaml"
GPU_REGISTER_FILE_GPU_UUIDS_KEY = "register_gpus"

GPU_FAKE_UUID = "GPU-Fake"

DDL_DEFAULT_LOG_FOLDER_NAME = "default"

###############################################################################

# <DB>

WORKER_REGISTRATION_TABLE_NAME = "worker_registration"
WORKER_REGISTRATION_TABLE_COMMAND = """
CREATE TABLE {} (
    workder_uuid VARCHAR(255) PRIMARY KEY,
    passcode VARCHAR(255) NOT NULL,
    workdir TEXT NOT NULL,
    logdir TEXT NOT NULL,
    port INTEGER NOT NULL
    gpu_uuid VARCHAR(255) NOT NULL
)
""".format(WORKER_REGISTRATION_TABLE_NAME)

WORKER_REGISTER_COMMAND = """
INSERT INTO {}(workder_uuid, passcode, workdir, logdir, port, gpu_uuid)
VALUES(%s, %s, %s, %s, %d, %s);
""".format(WORKER_REGISTRATION_TABLE_NAME)

WORKER_QUERY_REGIDTRATION_COMMAND = """
SELECT workder_uuid, passcode, workdir, logdir, port, gpu_uuid
FROM {}
""".format(WORKER_REGISTRATION_TABLE_NAME)

###############################################################################

def get_nvidia_gpu_mappings():
    command = ["nvidia-smi", "--query-gpu=index,gpu_uuid", "--format=csv,noheader"]
    try:
        exec_process = subprocess.Popen(command,
                                        stdout=subprocess.PIPE,
                                        stderr=subprocess.STDOUT)

        stdout, stderr = exec_process.communicate()
    except Exception as e:
        print("[Error::FATAL] Cannot get nvidia GPU uuid to id mapping: {}".format(str(e)))
        return {}

    if stderr is not None:
        print("[Error::FATAL] Cannot get nvidia-smi output: {}".format(stderr))
        return {}

    if stdout is None:
        print("[Error::FATAL] Cannot get nvidia GPU uuid to id mapping")
        return {}

    mappings = stdout.decode("utf-8").split('\n')
    uuid_to_id = {}
    for mapping in mappings:
        values = mapping.split(',')
        if len(values) != 2:
            continue
        uuid_to_id[values[1].strip()] = values[0].strip()

    return uuid_to_id


def gpu_uuid_to_gpu_id(runtime, gpu_uuid):
    if runtime[RUNTIME_CPU_MODE_KEY] and gpu_uuid == GPU_FAKE_UUID:
        return True, -1

    if gpu_uuid in runtime[RUNTIME_GPU_UUID_TO_ID_KEY]:
        return True, runtime[RUNTIME_GPU_UUID_TO_ID_KEY][gpu_uuid]
    else:
        return False, None


def gpu_uuids_get_gpu_ids(runtime, gpu_uuids):
    gpu_uuids_ids = []
    for gpu_uuid in gpu_uuids:
        success, gpu_id = gpu_uuid_to_gpu_id(runtime, gpu_uuid)
        if not success:
            continue
        gpu_uuids_ids += [(gpu_uuid, gpu_id)]
    return gpu_uuids_ids


###############################################################################

def register_single_worker(toplevel_workdir,
                           toplevel_logdir,
                           master_server,
                           base_port,
                           secrete):
    port = base_port
    worker_num = 0
    while True:
        worker_workdir_name = "worker{}".format(worker_num)
        worker_workdir = os.path.join(toplevel_workdir, worker_workdir_name)
        if os.path.exists(worker_workdir):
            worker_num += 1
            continue
        os.mkdir(worker_workdir)
        break
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    while True:
        try:
            if port >= 65535:
                print("[Error] invalid port number: {}".format(port))
                return False, None, None, None, None

            s.bind(("127.0.0.1", port))
            s.close()
            print("[Register] found available port: {}".format(port))
            break
        except socket.error as e:
            port = ((port // 100) + 1) * 100
            if e.errno == errno.EADDRINUSE:
                continue
            else:
                # something else raised the socket.error exception
                print("[Error] {}".format(e))
                return False, None, None, None, None
        except Exception as e:
            print("[Error] uncaught error: {}".format(str(e)))
            return False, None, None, None, None

    default_log_dir = os.path.join(toplevel_logdir, DDL_DEFAULT_LOG_FOLDER_NAME)

    register_is_success, \
    worker_uuid, \
    worker_passcode = Worker.register(master_server, default_log_dir, secrete)
    if not register_is_success:
        print("[Error] worker failed to register")
        return False, None, None, None, None

    print("[Register] registered worker {}".format(worker_uuid))
    return True, worker_uuid, worker_passcode, worker_workdir, port


def register(runtime,
             metadir,
             toplevel_workdir,
             toplevel_logdir,
             secrete):

    # First, check if the GPU register file exists. Note that if running in CPU mode for
    # local debugging, then GPU register file is not required.
    gpu_register_file = os.path.join(metadir, GPU_REGISTER_FILE_NAME)
    if not runtime[RUNTIME_CPU_MODE_KEY]:
        if not os.path.exists(gpu_register_file):
            print("[Error::FATAL] Does not have a GPU register file. Cannot register workers.")
            return False

        # Parse the GPU register file to understand which GPUs should be registered.
        try:
            with open(gpu_register_file, "r") as f:
                gpu_register = yaml.load(f)
        except Exception as e:
            print("[Error::FATAL] Cannot parse GPU register file: {}".format(str(e)))
            return False

        # Validate the GPUs.
        gpu_uuids = gpu_register.get(GPU_REGISTER_FILE_GPU_UUIDS_KEY, None)
        if not gpu_uuids:
            print("[Error::FATAL] Do not have GPU for registration.")
            return False

        gpu_uuids_ids = gpu_uuids_get_gpu_ids(runtime, gpu_uuids)
        gpu_count = len(gpu_uuids_ids)
        if gpu_count == 0:
            print("[Error::FATAL] None of the registered GPUs is valid anymore.")
            return False
    else:
        # For local testing, fake to have 1 GPU.
        gpu_uuids_ids = [(GPU_FAKE_UUID, -1)]
        gpu_count = 1

    # Create the table that contains worker registration information.
    success, _ = create_table(WORKER_REGISTRATION_TABLE_COMMAND)
    if not success:
        print("[Error::FATAL] Failed to create worker registration table.")
        return False

    master_server = runtime[RUNTIME_MASTER_SERVER_KEY]
    print("Start worker registration")
    print("\t[master_server url]: {}".format(master_server))
    print("\t[toplevel working directory]: {}".format(toplevel_workdir))
    print("\t[meta directory]: {}".format(metadir))
    print("\t[secrete] : {}".format(secrete))

    port = 10000
    worker_registered = {}
    # Register all the workers.
    for (gpu_uuid, gpu_id) in gpu_uuids_ids:
        success, \
        workder_uuid, \
        worker_passcode, \
        worker_workdir, \
        worker_port = register_single_worker(
                        toplevel_workdir,
                        toplevel_logdir,
                        master_server,
                        port,
                        secrete)

        if not success:
            continue

        # Create a log folder for the worker.
        worker_logdir = os.path.join(toplevel_logdir, str(worker_uuid))
        os.mkdir(worker_logdir)

        # Keep track of the registered worker in the db.
        worker_config = (workder_uuid,
                         worker_passcode,
                         worker_workdir,
                         worker_logdir,
                         worker_port,
                         gpu_uuid,)

        save_worker_registration(worker_config)
        port = ((worker_port // 100) + 1) * 100
        if port >= 65535:
            print("[Error] Running out of port! Abort further registration!")
            break

    return True


def registered():
    # If there exists the worker registration table, then the workers have
    # been registered.
    success, exists = table_exists(WORKER_REGISTRATION_TABLE_NAME)

    # If the database is not available for some reason, it is fatal...
    if not success:
        print("[Error::FATAL] Cannot connect to DB server. Abort...")
        return False, None
    else:
        return True, exists


def get_registered_workers():
    success, worker_configs = query_from_table(WORKER_QUERY_REGIDTRATION_COMMAND)
    registerd_workers = {}
    for (workder_uuid, passcode, workdir, logdir, port, gpu_uuid) in worker_configs:
        registerd_workers[worker_uuid] = {
            'passcode': passcode,
            'workdir': workdir,
            'logdir': logdir,
            'port': port,
            'gpu_uuid': gpu_uuid
        }

    return registerd_workers


def save_worker_registration(config):
    insert_table(WORKER_REGISTER_COMMAND, config)
    return


###############################################################################

def load_worker_runtime(debug_mode, cpu_mode):
    runtime = {}
    if debug_mode:
        runtime[RUNTIME_MASTER_SERVER_KEY] = "http://dtf-masterserver-test.us-west-1.elasticbeanstalk.com"
    else:
        runtime[RUNTIME_MASTER_SERVER_KEY] = "http://dtf-masterserver-dev.us-west-1.elasticbeanstalk.com"

    gpu_uuid_to_id = get_nvidia_gpu_mappings()
    runtime[RUNTIME_GPU_UUID_TO_ID_KEY] = gpu_uuid_to_id
    runtime[RUNTIME_CPU_MODE_KEY] = cpu_mode
    return runtime