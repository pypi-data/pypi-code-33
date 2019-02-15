# config
DEBUG = False
FROM_S3 = True
UPLOAD_S3 = True
USE_COMPILED_CODE = False
CREATE_VENV_TIMEOUT = 30

ALLOWED_CODE_EXTENSION = ['.so', '.pyd', '.py']

ALLOWED_DATASET_EXTENSION = ['.tfrecords', '.csv', '.txt']

CODE_DIR_NAME = 'code'
DATASET_DIR_NAME = "dataset"
OUTPUT_DIR_NAME = "out"

TF_CONFIG = 'TF_CONFIG'

MODEL_WIN_OUT_DIR = ".model.win.out"
MODEL_LINUX_OUT_DIR = ".model.linux.out"

DATASET_TAR_GZ = 'dataset.tar.gz'

VENV = 'venv'

# OS types
LINUX = "linux"
WIN = "win"

# File marker name
WORKER_FAILED_MARKER = "worker_run_failed"

REQUIREMENTS_TXT = "requirements.txt"

# TEMP variables
NUMBER_GPU_WORKER = 4
NUMBER_CPU_WORKER = 1