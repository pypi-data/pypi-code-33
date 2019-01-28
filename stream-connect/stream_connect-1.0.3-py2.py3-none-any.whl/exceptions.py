class KafkaError(Exception):
    def __init__(self, message):
        """
        :param message: error message
        """
        self.message = message
        super(KafkaError, self).__init__(message)
