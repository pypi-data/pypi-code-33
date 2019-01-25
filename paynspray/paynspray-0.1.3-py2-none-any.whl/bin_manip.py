import struct

ENDIAN_LITTLE = 0
ENDIAN_BIG = 1

# Python 2/3 compatibility
try:
    from itertools import izip_longest
except ImportError:
    from itertools import zip_longest as izip_longest

def to_num(string, wrap = 60):
    code = struct.unpack("{}B".format(len(string)), string)
    buff = ""
    for byte in range(0, len(code)):
        if (byte % 15 == 0) and (len(buff) > 0):
            buff += "\r\n"
        buff += '0x{:02x}, '.format(code[byte])
    buff = buff.rstrip(', ')
    buff += "\r\n"
    return buff
    
def to_dword(string, wrap = 60):
    def each_slice(iterable, n, fillvalue = None):
        args = [iter(iterable)] * n
        return izip_longest(fillvalue = fillvalue, *args)
    
    code = string
    alignnr = len(string) % 4
    if (alignnr > 0):
        code += "\x00" * (4 - alignnr)
    codevalues = []
    for chars4 in each_slice(list(code), 4):
        chars4 = "".join(chars4)
        dwordvalue = struct.unpack("<L", chars4)
        codevalues.append(dwordvalue[0])
    buff = ""
    for byte in range(0, len(codevalues)):
        if (byte % 8 == 0) and (len(buff) > 0):
            buff += "\r\n"
        buff += '0x{:08x}, '.format(codevalues[byte])
    buff = buff.rstrip(', ')
    buff += "\r\n"
    return buff
    
def to_unescape(data, endian = ENDIAN_LITTLE, prefix = '%u'):
    if (len(data) % 2 != 0):
        data += "\x41"
    
    dptr = 0
    buff = ''
    while (dptr < len(data)):
        c1 = struct.unpack("{}B".format(len(data[dptr : dptr + 1])), data[dptr : dptr + 1])[0]
        dptr += 1
        c2 = struct.unpack("{}B".format(len(data[dptr : dptr + 1])), data[dptr : dptr + 1])[0]
        dptr += 1
        
        if (endian == ENDIAN_LITTLE):
            buff += "{}{:02x}{:02x}".format(prefix, c2, c1)
        else:
            buff += "{}{:02x}{:02x}".format(prefix, c1, c2)
            
    return buff

def pack_int64le(val):
    return struct.pack("<Q", val)
    
def ror(val, cnt):
    tmpbits = struct.pack(">L", val)
    bits = list(''.join('{0:08b}'.format(ord(x), 'b') for x in tmpbits))
    for c in range(1, cnt + 1):
        bits.insert(0, bits.pop())
        
    newbits = ''.join(str(x) for x in bits)
    tmpint = int(newbits, 2)
    tmpbytes = bytearray()
    while tmpint:
        tmpbytes.append(tmpint & 0xff)
        tmpint >>= 8
    
    retval = bytes(tmpbytes[::-1])
    while len(retval) < 4:
        retval = "\x00" + retval
    
    return struct.unpack(">L", retval)[0]
    
def rol(val, cnt):
    tmpbits = struct.pack(">L", val)
    bits = list(''.join('{0:08b}'.format(ord(x), 'b') for x in tmpbits))
    for c in range(1, cnt + 1):
        bits.append(bits.pop(0))
        
    newbits = ''.join(str(x) for x in bits)
    tmpint = int(newbits, 2)
    tmpbytes = bytearray()
    while tmpint:
        tmpbytes.append(tmpint & 0xff)
        tmpint >>= 8
    
    retval = bytes(tmpbytes[::-1])
    while len(retval) < 4:
        retval = "\x00" + retval
    
    return struct.unpack(">L", retval)[0]