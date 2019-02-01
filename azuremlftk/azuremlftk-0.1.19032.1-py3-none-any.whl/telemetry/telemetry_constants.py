class TelemetryConst:

    # Telemetry prefixes
    TELEMETRY_PREFIX_TATK = 'azureml.text'
    TELEMETRY_PREFIX_FTK = 'azureml.timeseries'
    TELEMETRY_PREFIX_CVTK = 'azureml.vision'

    MSG_PKG_INIT = "Initializing package "

    MSG_EXPERIMENT_FIT_START = "Fit starting in experiment "
    MSG_EXPERIMENT_FIT_END = "Fit finished in experiment "
    MSG_EXPERIMENT_FIT_FAIL = "Fit failed in experiment "
    
    MSG_EXPERIMENT_PREDICT_START = "Prediction starting in experiment "
    MSG_EXPERIMENT_PREDICT_END = "Prediction finished in experiment "
    MSG_EXPERIMENT_PREDICT_FAIL = "Prediction failed in experiment "

    MSG_DEPLOY_START = "Deploying model starts "
    MSG_DEPLOY_END = "Deploying model ends successfully "
    MSG_DEPLOY_FAIL = "Deploying model failed "
    MSG_DEPLOY_DELETE = "Deleting deployment "

    MSG_DATASET_SIZE = "Dataset Size"
    
    PREFIX = "prefix"
    LOG_MACHINE_INFO = 'log_machine_info'
    TELEMETRY_CLIENT_NAME = "telemetryclient"