

class EnvisionError(object):

    map = dict()
    map['INIT_MQTT_CLIENT_FAILED'] = {'code': -100, 'msg': 'INIT_MQTT_CLIENT_FAILED'}
    map['MQTT_CLIENT_CONNECT_FAILED'] = {'code': -101, 'msg': 'MQTT_CLIENT_CONNECT_FAILED'}
    map['MQTT_CLIENT_PUBLISH_FAILED'] = {'code': -102, 'msg': 'MQTT_CLIENT_PUBLISH_FAILED'}
    map['MQTT_CLIENT_DISCONNECT_FAILED'] = {'code':-103, 'msg': 'MQTT_CLIENT_DISCONNECT_FAILED'}
    map['MQTT_CLIENT_SUBSCRIEBE_FAILED'] = {'code':-104, 'msg': 'MQTT_CLIENT_SUBSCRIEBE_FAILED'}
    map['MQTT_CLIENT_CLOSE_FAILED'] = {'code':-105, 'msg': 'MQTT_CLIENT_CLOSE_FAILED'}
    map['INVALID_DEVICE_CREDENTIAL'] = {'code':-106, 'msg': 'INVALID_DEVICE_CREDENTIAL'}
    map['INVALID_REPLY_MESSAGE_FORMAT'] = {'code':-107, 'msg': 'INVALID_REPLY_MESSAGE_FORMAT'}
    map['INVALID_PAYLOAD'] = {'code':-108, 'msg': 'INVALID_PAYLOAD'}
    map['EMPTY_PAYLOAD'] = {'code':-109, 'msg': 'EMPTY_PAYLOAD'}
    map['GET_LOCAL_MODEL_FAILED'] = {'code':-110, 'msg': 'GET_LOCAL_MODEL_FAILED'}
    map['MODEL_VALIDATION_FAILED'] = {'code':-111, 'msg': 'MODEL_VALIDATION_FAILED'}
    map['RESPONSE_PARSE_ERR'] = {'code':-112, 'msg': 'RESPONSE_PARSE_ERR'}
    map['MQTT_RESPONSE_PARSED_FALED'] = {'code':-113, 'msg': 'MQTT_RESPONSE_PARSED_FALED'}
    map['UNSUPPPORTED_REQUEST_CALL_TYPE'] = {'code':-114, 'msg': 'UNSUPPPORTED_REQUEST_CALL_TYPE'}
    map['SESSION_IS_NULL'] = {'code':-115, 'msg': 'SESSION_IS_NULL'}
    map['STATUS_IS_UNKNOWN'] = {'code':-116, 'msg': 'STATUS_IS_UNKNOWN'}
    map['CODE_ERROR_MISSING_ARGS'] = {'code':-117, 'msg': 'CODE_ERROR_MISSING_ARGS'}
    map['CODE_ERROR_ARG_INVALID'] = {'code':-118, 'msg': 'CODE_ERROR_ARG_INVALID'}
    map['CANNOT_REGISTER_CALLBACK'] = {'code':-119, 'msg': 'CANNOT_REGISTER_CALLBACK'}
    map['DEVICE_SESSION_IS_NULL'] = {'code':-120, 'msg': 'SESSION IS NULL'}
    map['CALLBACK_EXECUTION_FAILED'] = {'code':-121, 'msg': 'callback execution failed'}
    map['STATUS_ERROR'] = {'code':-122, 'msg': 'invalid operation in current status'}
    map['STATUS_NOT_ALLOW_LOGIN'] = {'code':-123, 'msg': 'status not allow login'}
    map['STATUS_NOT_ALLOW_LOGOUT'] = {'code':-124, 'msg': 'status not allow logout'}
    map['FUTURE_TASK_TIME_OUT'] = {'code':-125, 'msg': 'sync request timeout'}

    map['SUCCESS'] = {'code':0, 'msg': 'success'}

    @classmethod
    def getErrorCode(cls, key):
        return cls.map[key]['code']

    @classmethod
    def getErrorMessage(cls, key):
        return cls.map[key]['msg']