from core.exception.EnvisionException import EnvisionException
from core.exception.EnvisionError import EnvisionError


class CheckUtil(object):

    @classmethod
    def checkNotEmpty(cls, string ,fieldName):
        if cls.isEmpty(string) :
            raise EnvisionException('sdk-client exception: %s is mandatory' % fieldName,
                                    EnvisionError.getErrorCode('CODE_ERROR_MISSING_ARGS'))

    @classmethod
    def isEmpty(cls, str):
        return str is None or len(str) <= 0