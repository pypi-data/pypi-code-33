from worker.worker_start import *
from main.utils import RUNTIME_MASTER_SERVER_KEY

def worker_entry(runtime, workdir, metadir, port, worker_uuid, gpu_id):
    worker = Worker(runtime[RUNTIME_MASTER_SERVER_KEY],
                    port,
                    workdir,
                    metadir,
                    worker_uuid=worker_uuid,
                    gpu_id=gpu_id)

    while True:
        enroll_is_success = worker.enroll()
        if not enroll_is_success:
            raise RuntimeError("enroll failed")
        while True:
            poll_is_success, enroll_again = worker.poll()
            if not poll_is_success:
                if enroll_again:
                    # break polling loop and enroll again
                    break
                else:
                    raise RuntimeError("poll failed")