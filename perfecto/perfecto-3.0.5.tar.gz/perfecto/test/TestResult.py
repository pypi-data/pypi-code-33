class TestResult:
    def __init__(self):
        pass

    def is_successful(self):
        raise NotImplementedError

    def get_message(self):
        raise NotImplementedError


class TestResultSuccess(TestResult):
    status = 'PASSED'

    def is_successful(self):
        return True

    def get_message(self):
        return self.status


class TestResultFailure(TestResult):
    status = 'FAILED'

    def __init__(self, reason, exception=None, failureReason=None):

        if exception is not None:
            self.message = str(reason) + ': ' + str(exception)
        else:
            self.message = reason

        if len(self.message) > 4096:
            self.message = self.message[:4096]
        
        if failureReason is not None:
            self.failureReason = failureReason
        else:
            self.failureReason = None

    def is_successful(self):
        return False

    def get_message(self):
        return self.message

    def get_failureReason(self):
        return self.failureReason
