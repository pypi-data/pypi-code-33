from .decorators.argIsType import argIsType


@argIsType(str)
def endsWith(prefix):
    @argIsType(str)
    def endsWith_inner(fullStr):
        return fullStr.endswith(prefix)

    return endsWith_inner
