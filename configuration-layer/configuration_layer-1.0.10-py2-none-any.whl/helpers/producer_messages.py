def operation_result(**kwargs):
    return {
        "value": {
            "service_name": kwargs.get('service_name', None),
            "last_operation": kwargs.get('last_operation', None),
            "timestamp": kwargs.get('timestamp', None),
            "operation_result": kwargs.get('operation_result', None),
            "operation_description":kwargs.get('operation_description', ''),
            "error_description":kwargs.get('error_description','')
        },
        "key": {
            "service_name": kwargs.get('service_name', None),

        }

    }


def const_values():
    return {
        "SUCCESS": "SUCCESS",
        "FAIL": "FAIL",
        "CONFIGURATION_FILE_VALIDATION_ERROR":'CONFIGURATION_FILE_VALIDATION_ERROR',
        "PENDING":"PENDING"

    }
