

class DeliveryTopicFormat(object):
    MEASUREPOINT_POST = "/sys/{}/{}/thing/measurepoint/post"
    EVENT_POST = "/sys/{}/{}/thing/event/{}/post"
    TSL_TEMPLATE_GET = "/sys/{}/{}/thing/tsltemplate/get"
    MODEL_UP_RAW = "/sys/{}/{}/thing/model/up_raw"

    SUB_DEVICE_REGISTER_TOPIC_FMT = "/sys/{}/{}/thing/device/register"

    TOPO_GET_TOPIC_FMT = "/sys/{}/{}/thing/topo/get"
    TOPO_DELETE_TOPIC_FMT = "/sys/{}/{}/thing/topo/delete"
    TOPO_ADD_TOPIC_FMT = "/sys/{}/{}/thing/topo/add"

    SUB_DEVICE_LOGIN_TOPIC_FMT = "/ext/session/{}/{}/combine/login"
    SUB_DEVICE_LOGOUT_TOPIC_FMT = "/ext/session/{}/{}/combine/logout"

    TAG_DELETE_TOPIC_FMT = "/sys/{}/{}/thing/tag/delete"
    TAG_UPDATE_TOPIC_FMT = "/sys/{}/{}/thing/tag/update"

    PROGRESS_REPORT_TOPIC_FMT = "/sys/{}/{}/ota/device/progress"
    VERSION_REPORT_TOPIC_FMT = "/sys/{}/{}/ota/device/inform"
    UPDATE_REQUEST_TOPIC_FMT = "/sys/{}/{}/ota/device/request"

    ATTRIBUTE_UPDATE = "/sys/{}/{}/thing/attribute/update"
    ATTRIBUTE_QUERY = "/sys/{}/{}/thing/attribute/query"
    ATTRIBUTE_DELETE = "/sys/{}/{}/thing/attribute/delete"

    TAG_QUERY = "/sys/{}/{}/thing/tag/query"

    MEASUREPOINT_SET_REPLY = "/sys/{}/{}/thing/service/measurepoint/set_reply"
    SERVICE_INVOKE_REPLY = "/sys/{}/{}/thing/service/{}_reply"
    MODEL_DOWN_RAW_REPLY = "/sys/{}/{}/thing/model/down_raw_reply"
    MEASUREPOINT_GET_REPLY = "/sys/{}/{}/thing/service/measurepoint/get_reply"
    RRPC_REPLY = "/sys/{}/{}/rrpc/response/{}"

    ENABLE_DEVICE_REPLY = "/sys/{}/{}/thing/enable_reply"
    DISABLE_DEVICE_REPLY = "/sys/{}/{}/thing/disable_reply"
    DELETE_DEVICE_REPLY = "/sys/{}/{}/thing/delete_reply"

    SUB_DEVICE_ENABLE_REPLY = "/ext/session/{}/{}/combine/enable_reply"
    SUB_DEVICE_DISABLE_REPLY = "/ext/session/{}/{}/combine/disable_reply"
    SUB_DEVICE_DELETE_REPLY = "/ext/session/{}/{}/combine/delete_reply"

    DEVICE_OTA_REPLY = "/sys/{}/{}/ota/device/upgrade_reply"