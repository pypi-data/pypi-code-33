import hex, struct, wordwrap

DefaultWrap = 60

def to_python(string, wrap = DefaultWrap, name = "buf"):
    """Converts a raw string into a Python buffer"""
    return hex.hexify(string, wrap, "{} += \"".format(name), '"', "{} = \"\"\n".format(name), '"')

def to_python_comment(string, wrap = DefaultWrap):
    """Creates a Python comment"""
    return wordwrap.wordwrap(string, 0, wrap, '', '# ')

def to_c(string, wrap = DefaultWrap, name = "buf"):
    """Converts a raw string into a C-style byte array"""
    return hex.hexify(string, wrap, '"', '"', "unsigned char {}[] = \n".format(name), '";')

def to_c_comment(string, wrap = DefaultWrap):
    """Creates a C comment"""
    return "/*\n" + wordwrap.wordwrap(string, 0, wrap, '', ' * ') + " */\n"

def to_vbscript(string, name = "buf"):
    """Converts a raw string into a VBScript byte array"""
    if string is None or len(string) == 0:
        return "{}".format(name)

    code = struct.unpack("{}B".format(len(string)), string)
    buff = "{}=Chr({})".format(name, code[0])
    for byte in range(1, len(code)):
        if (byte % 100 == 0):
            buff += "\r\n{}={}".format(name, name)

        buff += "&Chr({})".format(code[byte])

    return buff

def to_vba(string, name = "buf"):
    """Converts a raw string into a VBA byte array"""
    if string is None or len(string) == 0:
        return "{} = Array()".format(name)

    code = struct.unpack("{}B".format(len(string)), string)
    buff = "{} = Array(".format(name)
    maxbytes = 80

    for idx in range(0, len(code)):
        buff += str(code[idx])
        if idx < len(code) - 1:
            buff += ","
        if (idx > 1 and (idx % maxbytes) == 0):
            buff += " _\r\n"

    buff += ")\r\n"

    return buff

