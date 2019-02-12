import hashlib

def md5(s):
    """
    返回字符串的md5值
    """
    if type(s) is not bytes:
        s = s.encode()
    h = hashlib.md5()
    h.update(s)
    return h.hexdigest()