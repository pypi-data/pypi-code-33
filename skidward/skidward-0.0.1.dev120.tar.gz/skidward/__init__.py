from enum import Enum

from dotenv import load_dotenv


load_dotenv(verbose=True)


class JobStatus(Enum):
    READY = "ready"
    RUNNING = "running"
    SUCCESS = "success"
    FAIL = "fail"
