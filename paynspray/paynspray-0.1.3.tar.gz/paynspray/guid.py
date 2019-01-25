import binascii

def to_guid(bytes):
    """Converts a 16 byte string to a GUID"""
    if bytes is None:
        return None
        
    s = binascii.hexlify(bytes)
    parts = [s[6:8] + s[4:6] + s[2:4] + s[0:2], s[10:12] + s[8:10], s[14:16] + s[12:14], s[16:20], s[20:32]]
    
    return "{" + '-'.join(parts) + "}"