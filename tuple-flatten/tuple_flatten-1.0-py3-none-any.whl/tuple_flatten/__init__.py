def flatten(*argv):
    res = None
    for t in argv:
        if res is None:
            res = t
        else:
            for i in range(len(t)):
                res = res[:i] + (res[i]+t[i], ) + res[1+i:]
    return res


