class BaseResult: 
    """A generic result object"""
    
    def __init__(self, failed, status_code, message, data):
        self.failed = failed
        self.status_code = status_code
        self.message = message
        self.data = data