from hs_infra.utils.base_utils import BaseUtils
from hs_infra.utils.date_time_utils import DateTimeUtils
from hs_infra.utils.string_utils import StringUtils


class Utils(BaseUtils,
            DateTimeUtils,
            StringUtils,):

    @classmethod
    def wrap_response(cls, response_error_enum_obj, body):
        response_dict = dict()
        response_dict['status'] = response_error_enum_obj.status
        response_dict['code'] = response_error_enum_obj.code
        response_dict['message'] = response_error_enum_obj.message
        response_dict['body'] = body
        return response_dict
