from dobby.results.base_result import BaseResult


class SuccessResult(BaseResult):

    def __init__(self, status_code=200, message='', data={}):
        super().__init__(False, status_code, message, data)
