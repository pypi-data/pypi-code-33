import struct

def xor(key, buffer):
    """Returns an XOR encoded buffer"""
    if type(key) == int:
        xor_key = int(key)
    elif type(key) == NoneType:
        xor_key = 0
    else:
        xor_key = int(key, 16)

    if not (0 <= xor_key <= 255):
        raise ValueError("XOR key must be a value between 0 and 255")

    buf = ''

    for byte in bytearray(buffer):
        xor_byte = byte ^ xor_key
        buf += struct.pack('B', xor_byte)

    return buf

    