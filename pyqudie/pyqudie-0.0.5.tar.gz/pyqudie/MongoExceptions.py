'''MongoExceptions'''


class MongoExceptions(Exception):

    def __init__(self, *args):
        self.args = args


class NoDatabaseException(MongoExceptions):

    def __init__(self, message = 'No such Database!', code = 422, args = ('No such Database!',)):
        self.args = args
        self.message = message
        self.code = code


class InvalidArgumentsException(MongoExceptions):

    def __init__(self, message = 'Invalid Arguments!', code = 422, args = ('Invalid Arguments!',)):
        self.args = args
        self.message = message
        self.code = code


class ConnectFailedException(MongoExceptions):

    def __init__(self, message = 'Authentication Required or Connection Error!', code = 422, args = ('Authentication Required or Connection Error!',)):
        self.args = args
        self.message = message
        self.code = code


class InvalidCollectionException(MongoExceptions):

    def __init__(self, message = 'Invalid Collection!', code = 422, args = ('Invalid Collection!',)):
        self.args = args
        self.message = message
        self.code = code


class InvalidQueryObjectException(MongoExceptions):

    def __init__(self, message = 'Invalid Query Object!', code = 422, args = ('Invalid Query Object!',)):
        self.args = args
        self.message = message
        self.code = code


class InvalidInsertObjectException(MongoExceptions):

    def __init__(self, message = 'Invalid Insert Object!', code = 422, args = ('Invalid Insert Object!',)):
        self.args = args
        self.message = message
        self.code = code


class InvalidRemoveQueryException(MongoExceptions):

    def __init__(self, message = 'Invalid Remove Query!', code = 422, args = ('Invalid Remove Query!',)):
        self.args = args
        self.message = message
        self.code = code


class InvalidRemoveOptionException(MongoExceptions):

    def __init__(self, message = 'Invalid Remove Option!', code = 422, args = ('Invalid Remove Option!',)):
        self.args = args
        self.message = message
        self.code = code


class RemoveAllNotConfirmedException(MongoExceptions):

    def __init__(self, message = 'Remove All not Confirmed!', code = 422, args = ('Remove All not Confirmed!',)):
        self.args = args
        self.message = message
        self.code = code


class OperationFailedException(MongoExceptions):

    def __init__(self, message = 'Operation Failed!', code = 422, args = ('Operation Failed!',)):
        self.args = args
        self.message = message
        self.code = code


class InvalidUpdateQueryException(MongoExceptions):

    def __init__(self, message = 'Invalid Update Query!', code = 422, args = ('Invalid Update Query!',)):
        self.args = args
        self.message = message
        self.code = code


class InvalidUpdateDictException(MongoExceptions):

    def __init__(self, message = 'Invalid Update Dict!', code = 422, args = ('Invalid Update Dict!',)):
        self.args = args
        self.message = message
        self.code = code


class InvalidUpdateOptionException(MongoExceptions):

    def __init__(self, message = 'Invalid Update Option!', code = 422, args = ('Invalid Update Option!',)):
        self.args = args
        self.message = message
        self.code = code


class InvalidObjectIdException(MongoExceptions):

    def __init__(self, message = 'Invalid ObjectId!', code = 422, args = ('Invalid ObjectId!',)):
        self.args = args
        self.message = message
        self.code = code
