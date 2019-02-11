# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

MMS_WORKSPACE_API_VERSION = '2018-11-19'
MMS_SYNC_TIMEOUT_SECONDS = 80
SUPPORTED_RUNTIMES = {'spark-py': 'SparkPython', 'python': 'Python', 'python-slim': 'PythonSlim'}
UNDOCUMENTED_RUNTIMES = ['python-slim']
WORKSPACE_RP_API_VERSION = '2018-11-19'
MAX_HEALTH_CHECK_TRIES = 30
HEALTH_CHECK_INTERVAL_SECONDS = 1
DOCKER_IMAGE_TYPE = "Docker"
UNKNOWN_IMAGE_TYPE = "Unknown"
FPGA_IMAGE_TYPE = "FPGA"
WEBAPI_IMAGE_FLAVOR = "WebApiContainer"
FPGA_IMAGE_FLAVOR = "BrainwavePackage"
IOT_IMAGE_FLAVOR = "IoTContainer"
UNKNOWN_IMAGE_FLAVOR = "Unknown"
CLOUD_DEPLOYABLE_IMAGE_FLAVORS = [WEBAPI_IMAGE_FLAVOR, FPGA_IMAGE_FLAVOR]
ARCHITECTURE_AMD64 = "amd64"
ARCHITECTURE_ARM32V7 = "arm32v7"
ACI_WEBSERVICE_TYPE = "ACI"
AKS_WEBSERVICE_TYPE = "AKS"
FPGA_WEBSERVICE_TYPE = "FPGA"
UNKNOWN_WEBSERVICE_TYPE = "Unknown"
CLI_METADATA_FILE_WORKSPACE_KEY = 'workspaceName'
CLI_METADATA_FILE_RG_KEY = 'resourceGroupName'
MODEL_METADATA_FILE_ID_KEY = 'modelId'
IMAGE_METADATA_FILE_ID_KEY = 'imageId'
