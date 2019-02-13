from performance import DEBUG


def logd(log='', e=None):
    if DEBUG:
        print(log)
    if e is not None:
        assert isinstance(e, Exception)
        print(e)


def tip(log='', e=None):
    if e is not None:
        assert isinstance(e, Exception)
        print(e)
    print(log)



