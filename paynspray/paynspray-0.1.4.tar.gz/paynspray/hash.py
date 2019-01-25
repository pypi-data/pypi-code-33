import hashlib

def md5_raw(string):
    """Returns the MD5 digest of the provided string as raw binary"""
    m = hashlib.md5()
    m.update(string)
    return m.digest()
    
def md5(string):
    """Returns the MD5 digest of the provided string as a hexadecimal string"""
    m = hashlib.md5()
    m.update(string)
    return m.hexdigest()
    
def sha1_raw(string):
    """Returns the SHA1 digest of the provided string as raw binary"""
    s = hashlib.sha1()
    s.update(string)
    return s.digest()
    
def sha1(string):
    """Returns the SHA1 digest of the provided string as a hexadecimal string"""
    s = hashlib.sha1()
    s.update(string)
    return s.hexdigest()

def sha256_raw(string):
    """Returns the SHA256 digest of the provided string as raw binary"""
    s = hashlib.sha256()
    s.update(string)
    return s.digest()

def sha256(string):
    """Returns the SHA256 digest of the provided string as a hexadecimal string"""
    s = hashlib.sha256()
    s.update(string)
    return s.hexdigest()