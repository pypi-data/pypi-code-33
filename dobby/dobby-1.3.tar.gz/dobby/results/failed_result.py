from dobby.results.base_result import BaseResult


class FailedResult(BaseResult):

    def __init__(self, error_message, status_code=400, data={}):
        super().__init__(True, status_code, error_message, data)
