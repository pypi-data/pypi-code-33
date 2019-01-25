import hex, HTMLParser, random, re, struct

def uri_encode(string, mode = 'hex-normal'):
    """Encodes a string for use in HTTP URIs and parameters"""
    if string is None:
        return ""
        
    if mode == 'none':
        return string
        
    all = r'.'
    noslashes = r'[^\/\\]+'
    normal = r'[^a-zA-Z0-9\/\\\.\-_~]+'
    
    if mode == 'hex-all':
        return re.sub(all, lambda s: hex.to_hex(s.group(), '%'), string)
    elif mode == 'hex-normal':
        return re.sub(normal, lambda s: hex.to_hex(s.group(), '%'), string)
    elif mode == 'hex-noslashes':
        return re.sub(noslashes, lambda s: hex.to_hex(s.group(), '%'), string)
    elif mode == 'hex-random':
        res = ''
        for c in bytearray(string):
            b = chr(c)
            if (random.randrange(2) == 0):
                b = re.sub(all, lambda s: hex.to_hex(s.group(), '%'), b)
                res += b
            else:
                b = re.sub(normal, lambda s: hex.to_hex(s.group(), '%'), b)
                res += b
        return res
    else:
        raise ValueError("Invalid mode '{}'".format(mode))

def html_encode(string, mode = 'hex'):
    """Encodes a string for use in HTTP URIs and parameters"""
    if mode == 'hex':
        return "".join(map(lambda i: "&#x" + "{:02x}".format(i) + ";", struct.unpack('{}B'.format(len(string)), string)))
    elif mode == 'int':
        return "".join(map(lambda i: "&#" + str(i) + ";", struct.unpack('{}B'.format(len(string)), string)))
    elif mode == 'int-wide':
        return "".join(map(lambda i: "&#" + ("0" * (7 - len(str(i)))) + str(i) + ";", struct.unpack('{}B'.format(len(string)), string)))
    else:
        raise ValueError("Invalid mode '{}'".format(mode))

def html_decode(string):
    """Decodes an HTML encoded string"""
    return HTMLParser.HTMLParser().unescape(string)
