#
# assigns dict key-values onto self as attributes
# return secondaryObj
#   ** mutates secondaryObj
#


def mAssignToSelf(aDict, aSelf):
    for k, v in aDict.items():
        setattr(aSelf, k, v)

    return aSelf
