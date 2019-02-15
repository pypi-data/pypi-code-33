import json, yaml
import os
import shutil
import subprocess
from os.path import exists, join, basename, realpath, dirname
from requests import get
from sys import platform
from time import sleep

from common.TrainingTask import TrainingTask
from common.global_variable import *
from common.util.common_utils import TokenAuth, copytree, request_server, unzip_tarfile
from common.util.s3_utils import create_s3_client, s3_path_join
from worker.worker_log.worker_logger import worker_logger
from worker.worker_util.worker_util import download_file_from_s3, upload_output

os_platform = None
if platform.startswith("linux"):
    os_platform = LINUX
elif platform.startswith("win"):
    os_platform = WIN
else:
    raise Exception("{} is not supported".format(str(platform)))

class TaskContext(object):

    exec_process = None
    retry_count = 10
    workdir = None

    def __init__(self, exec_process, logger, workdir):
        self.exec_process = exec_process
        self.logger = logger
        self.workdir = workdir

    def flush_from_exec_process_queue(self):
        alive = True if self.exec_process.poll() is None else False
        # Flush the queue
        graceful = True
        failure_path = join(self.workdir, WORKER_FAILED_MARKER)
        if exists(failure_path):
            graceful = False
            with open(failure_path, "r") as f:
                self.logger.log_error("TaskContext", "flush_from_exec_process_queue error: {}".format(f.read()))

        return alive, graceful

    def terminate(self):
        if True if self.exec_process.poll() is None else False:
            self.exec_process.kill()

        return

    def can_retry(self):
        if self.retry_count <= 0:
            return False

        self.retry_count -= 1
        return True


class Worker:
    # local ip and port
    valid_until = None
    auth_token = None
    register_file = "register_"
    register_file_extension = ".yaml"
    worker_type = None
    resource_id = None
    last_error = None
    worker_logger = None
    temp_token = None
    tensorboard_process = None

    def __init__(self,
                 master_endpoint,
                 port,
                 workdir,
                 logdir,
                 worker_uuid=None,
                 gpu_id=-1):

        # local endpoint http://127.0.0.1:8000
        self.master_endpoint = master_endpoint
        self.port = port
        self.workdir = workdir
        self.logdir = logdir
        self.worker_logger = worker_logger(os.getpid(), logdir)
        self.resource_id = gpu_id
        self.worker_uuid = worker_uuid

    # register worker to create account
    # return {success}, {uuid}
    @classmethod
    def register(cls, master_endpoint, logdir, secrete=None):
        register_logger = worker_logger(os.getpid(), logdir)
        request_body = {"machine_spec_cpu" : 0, "machine_spec_gpu" : 1}
        if secrete is not None:
            request_body["secrete"] = secrete

        success, status_code, response_body, error_message = request_server(
            master_endpoint + "/api/v1/worker/register/",
            'post',
            **{"data": request_body})

        if not success:
            register_logger.log_error("register", error_message)
            return False, None, None

        if status_code == 200:
            uuid = response_body.get("uuid", None)
            if not uuid:
                register_logger.log_error("register", "unexpected uuid from server")
                return False, None, None

            register_logger.log_info("register", "worker uuid: {0}".format(uuid))
            passcode = response_body.get("passcode", None)
            if not uuid:
                register_logger.log_error("register", "unexpected passcode from server")
                return False, None, None

            register_logger.worker_id = uuid
            register_logger.worker_type = config["type"]
            register_logger.resource_id = gpu_uuid
            register_logger.log_info("register", "worker register succeed")
            return True, uuid, passcode
        else:
            register_logger.log_error("register", "status {0}, error '{1}'".format(
                                      status_code,
                                      response_body.get("error")))

            return False, None, None

    # enroll to master server to login and get auth token
    # return {success}
    def enroll(self, config):
        if self.worker_uuid is None:
            self.worker_logger.log_error("enroll", "missing worker uuid")
            return False

        # Get uuid of the worker, update the logger.
        self.worker_logger.worker_id = self.worker_uuid

        # Get type of the worker, update the logger.
        if "type" not in config:
            self.worker_logger.log_error("enroll", "cannot find type for the worker")
            return False

        worker_type = config["type"]
        if worker_type != "cpu" and worker_type != "gpu":
            self.worker_logger.log_error("enroll", "unexpected type for the worker: {}".format(worker_type))
            return False

        self.worker_type = worker_type
        self.worker_logger.worker_type = self.worker_type
        self.worker_logger.resource_id = self.resource_id

        # Get passcode of the worker.
        if "passcode" not in config:
            self.worker_logger.log_error("enroll", "cannot find passcode for the worker")
            return False

        request_body = {'uuid': self.worker_uuid, 'passcode': config["passcode"]}
        success, status_code, response_body, error_message = request_server(
            self.master_endpoint + "/api/v1/worker/enroll/",
            'post',
            **{"data": request_body})

        if not success:
            self.worker_logger.log_error("enroll", error_message)
            return False

        if status_code == 200:
            auth_token = response_body.get('auth_token', None)
            if not auth_token:
                self.worker_logger.log_error("enroll", "no auth token from server")
                return False

            self.auth_token = TokenAuth(auth_token)
            self.worker_logger.log_info("enroll", "success")
            return True
        else:
            self.worker_logger.log_error("enroll",
                                         "status code {0}, error {1}".format(status_code, response_body.get("error")))
            return False

    # after the first poll, keep polling for new task
    # return {success}, {enroll_again}
    def poll(self):
        if self.auth_token is None:
            self.worker_logger.log_error("poll", "worker has no auth token, need enroll")
            return False, True

        request_body = {'port': self.port}

        # Poll until a task is assigned to the worker
        while True:
            success, status_code, response_body, error_message = request_server(
                self.master_endpoint + "/api/v1/worker/poll/",
                'post',
                **{"data": request_body,
                   "auth": self.auth_token})

            if not success:
                self.worker_logger.log_error("poll", error_message)
                return False, False

            if status_code == 202:
                # task is not ready yet
                self.worker_logger.log_info("poll", "no task is ready for the worker")
                sleep(30)
            else:
                break

        # OK when task should be kicked off
        if status_code == 200:
            self.worker_logger.log_info("poll", "task is ready for the worker")

            # Validate the API response is as expected
            keys = ["task_uuid", "signal_finish", "ask_finish", "keep_alive_interval", "config",
                    "access_key_id", "secret_access_key", "session_token", "expiration", "s3_region", "s3_bucket_name"]
            for key in keys:
                if key not in response_body:
                    self.worker_logger.log_error("poll", "no {} from server".format(key))
                    return False, False

            config = response_body.get("config", None)
            try:
                task_config = json.loads(config)
            except Exception as e:
                self.worker_logger.log_error("poll", "unexpected task config format from server: {}".format(str(e)))
                return False, False

            task_uuid = response_body.get("task_uuid", None)
            if task_uuid is None:
                self.worker_logger.log_error("poll", "task_uuid is expect to be not None")
            keep_alive_interval = response_body.get("keep_alive_interval", None)
            if keep_alive_interval is None:
                self.worker_logger.log_error("poll", "keep_alive_interval is expect to be not None")
                return False, False
            signal_finish = response_body.get("signal_finish", None)
            if signal_finish is None:
                self.worker_logger.log_error("poll", "signal_finish is expect to be not None")
                return False, False
            ask_finish = response_body.get("ask_finish", None)
            if ask_finish is None:
                self.worker_logger.log_error("poll", "ask_finish is expect to be not None")
                return False, False

            if int(signal_finish) and int(ask_finish):
                self.worker_logger.log_error("poll", "unexpected task needs both signal and ask finish from server")
                return False, False

            # Validate s3 temp token
            access_key_id = response_body.get("access_key_id", None)
            if access_key_id is None:
                self.worker_logger.log_error("poll", "access_key_id is expect to be not None")
                return False, False

            secret_access_key = response_body.get("secret_access_key", None)
            if secret_access_key is None:
                self.worker_logger.log_error("poll", "secret_access_key is expect to be not None")
                return False, False

            session_token = response_body.get("session_token", None)
            if session_token is None:
                self.worker_logger.log_error("poll", "session_token is expect to be not None")
                return False, False

            expiration = response_body.get("expiration", None)
            if expiration is None:
                self.worker_logger.log_error("poll", "expiration is expect to be not None")
                return False, False

            s3_region = response_body.get("s3_region", None)
            if s3_region is None:
                self.worker_logger.log_error("poll", "s3_region is expect to be not None")
                return False, False

            s3_bucket_name = response_body.get("s3_bucket_name", None)
            if s3_bucket_name is None:
                self.worker_logger.log_error("poll", "s3_bucket_name is expect to be not None")
                return False, False

            self.temp_token = {
                'access_key_id': access_key_id,
                'secret_access_key': secret_access_key,
                'session_token': session_token,
                'expiration': expiration,
                's3_region': s3_region,
                's3_bucket_name' : s3_bucket_name
            }

            # Validate task config from server
            if "job_name" not in task_config:
                self.worker_logger.log_error("poll", "unexpected task config from server: no job_name")
                return False, False

            if task_config["job_name"] != "worker" and task_config["job_name"] != "ps":
                self.worker_logger.log_error("poll", "unexpected task config from server: unexpected job_name: {}".format(task_config["job_name"]))
                return False, False

            try:
                task = TrainingTask(**task_config)
            except Exception as e:
                self.worker_logger.log_error("poll", "unexpected task config from server: config, error: {}".format(str(e)))
                return False, False

            self.run(task_uuid, keep_alive_interval, signal_finish, task)
            return True, False
        if status_code == 401:
            self.worker_logger.log_error("poll", "auth_token expired. worker needs to enroll again")
            return False, True
        else:
            self.worker_logger.log_error("poll", "status code {0}, error {1}".format(status_code, response_body.get("error")))
            return False, False

    def fetch_code_and_data(self, task):
        assert isinstance(task, TrainingTask)

        # Cleanup workdir
        self.cleanup_workdir()

        # Download code to /workdir/CODE_DIR_NAME/
        self.download_code()

        # download dataset
        dataset_dir = join(self.workdir, DATASET_DIR_NAME)
        if exists(dataset_dir):
            shutil.rmtree(dataset_dir)

        # if the dataset exists (test), then keep the test dataset location
        # for ps task, task.dataset["dataset_location"] is None
        if task.dataset is not None and "dataset_location" in task.dataset and task.dataset["dataset_location"] is not None:
            if not exists(task.dataset["dataset_location"]):
                os.makedirs(dataset_dir)
                self.worker_logger.log_info("fetch_code_and_data", "downloading dataset from {}".format(task.dataset["dataset_location"]))
                download_file_from_s3(bucket_name, task.dataset["dataset_location"], dataset_dir, client)
                unzip_tarfile(join(dataset_dir, DATASET_TAR_GZ), dataset_dir)
            else:
                copytree(task.dataset["dataset_location"], dataset_dir, False, ALLOWED_DATASET_EXTENSION)

    # exec task
    def run(self, task_uuid, keep_alive_interval, signal_finish, task):
        self.worker_logger.log_info("run", "{} task: {}".format(task.job_name, task_uuid))
        self.fetch_code_and_data(task)

        if task.job_name == "worker":
            self.worker_logger.log_info("run", "task.model_location: {}".format(task.model_location))

        self.worker_logger.log_info("run", "workdir: {}".format(self.workdir))

        # create virtualenv
        path_env = join(self.workdir, VENV)
        create_env_process = subprocess.Popen(["python", "-m", VENV, path_env, "--system-site-packages"])
        create_env_process.wait(CREATE_VENV_TIMEOUT)
        if os_platform == WIN:
            python_path = join(path_env, "Scripts", "python")
        else:
            python_path = join(path_env, "bin", "python")

        # install requirements
        requirements_path = join(self.workdir, CODE_DIR_NAME, REQUIREMENTS_TXT)
        if exists(requirements_path):
            install_requirement_process = subprocess.Popen([python_path, "-m", "pip", "install", "-r", requirements_path])
            install_requirement_process.wait()

        # start running user code
        worker_run_path = join(dirname(realpath(__file__)), "worker_run.py")
        print("worker run path: {}".format(worker_run_path))
        exec_process = subprocess.Popen(
            [python_path, worker_run_path, str(self.workdir), str(task.job_name), str(task.task_index), str(task.cluster_spec),
             str(self.resource_id), str(self.worker_type), str(task_uuid)])

        task_context = TaskContext(exec_process, self.worker_logger, self.workdir)
        # get job_id from task.model_location
        job_id = task.model_location.split('/')[0]

        # Monitor the exec process and keep alive with server
        self.signal(task_context,
                    job_id,
                    task_uuid,
                    signal_finish,
                    keep_alive_interval)

        exec_process.wait()

        # upload training output
        # get temp access token by enroll and refresh temp token again
        if exists(join(self.workdir, OUTPUT_DIR_NAME)) and not DEBUG:
            self.enroll()
            self.worker_logger.log_info("run", "start uploading training artifacts")
            is_success = self.poll_temp_token(job_id)
            if is_success:
                upload_output(join(self.workdir, OUTPUT_DIR_NAME), job_id, self.temp_token)
        else:
            self.worker_logger.log_error("run", "failed to finish user training")

        # try to clean up work dir after run
        self.tensorboard_process.kill()
        self.cleanup_workdir()
        return

    def signal(self, task_context, job_id, task_uuid, signal_finish, keep_alive_interval):
        already_terminated = False
        alive = False
        request_body = {}
        while True:
            if not already_terminated:
                alive, graceful = task_context.flush_from_exec_process_queue()

            if alive and graceful:
                self.worker_logger.log_info("signal", "worker is still running on task {}".format(task_uuid))
                request_body = {'task_uuid': task_uuid, 'action': 'progress'}
                success, status_code, response_body, error_message = request_server(
                    self.master_endpoint + "/api/v1/worker/task/",
                    'post',
                    **{"data": request_body,
                       "auth": self.auth_token})

                if not success:
                    self.worker_logger.log_error("signal", error_message)
                    # If the server has returned an unexpected response, there
                    # is really nothing can be done at the worker side other
                    # than signal kill the task process. Server will take care
                    # of the clean up.
                    self.worker_logger.log_info("signal", "worker status: stop")
                    task_context.terminate()
                    return

                if status_code == 200:
                    status = response_body.get("result", None)
                    create_tensorboard = response_body.get("create_tensorboard", None)
                    upload_log = response_body.get("upload_log", None)
                    if status == "continue":
                        self.worker_logger.log_info("signal", "worker status: continue")
                        if create_tensorboard:
                            # find an empty port that worker can use to create tensorboard
                            # but there is a bug in tensorboard that cannot log event using port other than 6006
                            port = 6006

                            # start tensorboard
                            self.tensorboard_process = subprocess.Popen(["tensorboard", "--logdir={}".format(join(self.workdir, OUTPUT_DIR_NAME))])

                            # report tensorboard api back to master server
                            request_body = {'tensorboard_created': 1}
                            success, _, response_body, error_message = request_server(
                                self.master_endpoint + "/api/v1/worker/task/{}/".format(task_uuid),
                                'put',
                                **{"data": request_body,
                                   "auth": self.auth_token})
                            if success:
                                self.worker_logger.log_info("signal",
                                                            "successfully started tensorboard at {}".format(response_body.get("tensorboard_url", None)))
                            else:
                                self.worker_logger.log_warning("signal",
                                                               "failed to start tensorboard with error: {}".format(error_message))

                        if upload_log:
                            upload_log_auth = response_body.get("upload_log_auth", None)
                            if upload_log_auth is None:
                                self.worker_logger.log_info("signal",
                                                            "server asks for worker log but does not provide auth token")
                            else:
                                # instruct the worker to upload the log if exists.
                                task_log_path = join(self.workdir, OUTPUT_DIR_NAME, "{}.log".format(task_uuid))
                                task_error_log_path = join(self.workdir, OUTPUT_DIR_NAME, "{}.error.log".format(task_uuid))
                                if exists(task_log_path):
                                    upload_log(task_log_path, job_id, upload_log_auth)

                                if exists(task_error_log_path):
                                    upload_log(task_error_log_path, job_id, upload_log_auth)

                        sleep(int(keep_alive_interval))
                        continue
                    else:
                        # Note that the server tells the work to stop, the worker
                        # does not need to signal finish.
                        if status != "stop":
                            self.worker_logger.log_error("signal", "unexpected worker status from server: {}".format(status))
                        self.worker_logger.log_info("signal", "terminate task {}".format(task_uuid))
                        task_context.terminate()
                        return
                elif status_code < 500:
                    self.worker_logger.log_error("signal", "unexpected response status: {}, error: {}"
                                   .format(status_code, response_body.get("error", None)))
                    self.worker_logger.log_info("signal", "terminate task {}".format(task_uuid))
                    task_context.terminate()
                    return
                else:
                    # If server side has a problem, there is nothing more can
                    # be done at the client side. Abort the current job.
                    self.worker_logger.log_error("signal", "unexpected server side error status: {}".format(status_code))
                    if task_context.can_retry():
                        self.worker_logger.log_info("signal", "server side unexpected error, retry... (chance left: {})"
                                      .format(task_context.retry_count))
                        sleep(int(keep_alive_interval))
                        continue
                    else:
                        self.worker_logger.log_info("signal", "terminate task {}".format(task_uuid))
                        task_context.terminate()
                        return
            else:
                # If the exec process has terminated already, check the output
                # queue to see if there is an item indicates that the task is
                # finished.
                already_terminated = True
                request_body = {}
                if graceful:
                    self.worker_logger.log_info("signal", "task {} finished".format(task_uuid))
                    # If the worker needs to signal finish, let the server know
                    # the task has gracefuly finished. Note that there is no
                    # need to check the return status after this call.
                    if signal_finish:
                        request_body = {'task_uuid': task_uuid, 'action': 'finished'}
                else:
                    self.worker_logger.log_error("signal", "task {} unexpectedly stopped".format(task_uuid))
                    # Let the server know the task has failed as the exec
                    # process unexpectedly terminated. Note that there is no
                    # need to check the return status after this call.
                    request_body = {'task_uuid': task_uuid, 'action': 'failed'}

                success = True
                status_code = 0
                if not graceful or signal_finish:
                    success, status_code, _, _ = request_server(
                        self.master_endpoint + "/api/v1/worker/task/",
                        'post',
                        **{"data": request_body,
                           "auth": self.auth_token})

                task_context.terminate()
                if success and status_code >= 500:
                    # If server side has an error, retry.
                    if task_context.can_retry():
                        self.worker_logger.log_info("signal", "server side unexpected error, retry... (chance left: {})".format(task_context.retry_count))
                        sleep(int(keep_alive_interval))
                        continue

                return

    def get_code_dir_location(self):
        return join(self.workdir, CODE_DIR_NAME)

    # use poll api to get temp access token
    # set to self.temp_token
    # return {success}
    def poll_temp_token(self, job_id):
        api_name = "poll_temp_token"
        if job_id is None:
            self.worker_logger.log_error(api_name, "worker has no auth token, need enroll")
            return False
        if self.auth_token is None:
            self.worker_logger.log_error(api_name, "worker has no auth token, need enroll")
            return False

        request_body = {'port': self.port,
                        'job_id': job_id}

        # Poll until a task is assigned to the worker
        retry = 3
        status_code, response_body = None, None
        while retry > 0:
            success, status_code, response_body, error_message = request_server(
                self.master_endpoint + "/api/v1/worker/poll/",
                'post',
                **{"data": request_body,
                   "auth": self.auth_token})

            if not success:
                self.worker_logger.log_error(api_name, error_message)

            if status_code >= 500:
                retry -= 1
                sleep(10)
            else:
                break

        # OK when task should be kicked off
        if status_code == 200:
            self.worker_logger.log_info(api_name, "successfully poll temp token")
            self.temp_token = {
                'access_key_id': response_body.get("access_key_id", None),
                'secret_access_key': response_body.get("secret_access_key", None),
                'session_token': response_body.get("session_token", None),
                'expiration': response_body.get("expiration", None),
                's3_region': response_body.get("s3_region", None),
                's3_bucket_name': response_body.get("s3_bucket_name", None)
            }
            return True
        else:
            self.worker_logger.log_error(api_name, "failed to poll temp token: {}"
                                         .format(response_body.get("error", None)))
            return False

    def cleanup_workdir(self):
        for item in os.listdir(self.workdir):
            path = join(self.workdir, item)
            if os.path.isfile(path):
                os.remove(path)
            else:
                shutil.rmtree(path, ignore_errors=True)

    def download_code(self):
        code_dir = self.get_code_dir_location()
        os.makedirs(code_dir)
        client = create_s3_client(self.temp_token)
        bucket_name = self.temp_token['s3_bucket_name']
        if USE_COMPILED_CODE:
            if LINUX in os_platform:
                task_location = s3_path_join(task.model_location, MODEL_LINUX_OUT_DIR)
            elif WIN in os_platform and DEBUG:
                # allow windows machine to do local test
                # windows machine will have local win_out from pipeline server
                task_location = s3_path_join(task.model_location, MODEL_WIN_OUT_DIR)
            else:
                self.worker_logger.log_error("fetch_code_and_data", "unsupported os platform: {}".format(platform))
                return

            self.worker_logger.log_info("fetch_code_and_data", "downloading model from {}".format(task_location))
            download_file_from_s3(bucket_name, task_location, code_dir, client)

        else:
            # download the code tar directly
            download_file_from_s3(bucket_name, task.model_location, code_dir, client)
            unzip_tarfile(join(code_dir, DATASET_TAR_GZ), code_dir)

        return

    def download_dataset(self):
        pass

