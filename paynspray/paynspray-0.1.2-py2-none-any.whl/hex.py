import binascii, re, struct

DefaultWrap = 60

def to_hex(string, prefix = "\\x", count = 1):
    """Returns the hex version of the provided string"""
    """The count parameter defines the bytes per character (default: 1 byte)"""
    if ((len(string) % count) > 0):
        raise RuntimeError("Unable to chunk into {} byte chunks".format(count))
    
    return re.sub(r".{" + str((count * 2)) + "}", lambda s: prefix + s.group(), binascii.hexlify(string))

def to_hex_ascii(string, prefix = "\\x", count = 1, suffix = ""):
    """Returns the string with nonprintable ASCII characters converted to hex"""
    if ((len(string) % count) > 0):
        raise RuntimeError("Unable to chunk into {} byte chunks".format(count))

    def hex_block(s):
        if int(s, 16) in range(0x20, 0x7e + 1):
            return chr(int(s, 16))
        else:
            return prefix + s + str(suffix)

    return re.sub(r".{" + str((count * 2)) + "}", lambda s: hex_block(s.group()), binascii.hexlify(string))

def hex_to_raw(string):
    """Returns a raw string from a hex encoded string"""
    return binascii.unhexlify(string)

def hexify(string, col = DefaultWrap, line_start = '', line_end = '', buf_start = '', buf_end = ''):
    """Returns the hex version of the provided string (similar to to_hex(), but with word wrap support)"""
    output = buf_start
    cur = 0
    count = 0
    new_line = True

    for byte in bytearray(string):
        count += 1
        append = ''

        if (new_line == True):
            append += line_start
            new_line = False

        append += "\\x{:02x}".format(byte)
        cur += len(append)

        if ((cur + len(line_end) >= col) or (cur + len(buf_end) >= col)):
            new_line = True
            cur = 0

            if (count == len(string)):
                append += buf_end + "\n"
            else:
                append += line_end + "\n"

        output += append

    if (new_line == False):
        output += buf_end + "\n"

    return output

def hexdump(string, width = 16, base = 0):
    """Returns a hex dump of a string"""
    buf = ''
    idx = 0
    cnt = 0
    snl = False
    lst = 0
    lft_col_len = len("{:x}".format(int(base) + len(string)))
    if lft_col_len < 8:
        lft_col_len = 8

    while (idx < len(string)):
        chunk = string[idx:idx+width]
        addr = ("{:0" + "{}".format(lft_col_len) + "x}  ").format(int(base) + idx)
        line = " ".join(re.findall(r'..', binascii.hexlify(chunk)))
        buf += addr + line

        if lst == 0:
            lst = len(line)
            buf += (" " * 4)
        else:
            buf += (" " * abs(((lst - len(line)) + 4)))

        buf += "|"
        for c in struct.unpack("{}B".format(len(chunk)), chunk):
            if (c > 0x1f and c < 0x7f):
                buf += chr(c)
            else:
                buf += "."

        buf += "|\n"

        idx += width

    return buf + "\n"
        

def dehex(string):
    """Replaces hex-encoded characters with their ASCII equivalents"""
    if string is None:
        return string

    regex = r'\x5cx[0-9a-f]{2}'
    return re.sub(regex, lambda x: chr(int(x.group()[2:4], 16)), string, flags = re.M | re.I)
    