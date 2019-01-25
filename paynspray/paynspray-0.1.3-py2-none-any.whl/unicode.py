import basex, random, re, struct

def to_unicode(string = '', type = 'utf-16le', mode = '', size = ''):
    """Converts ASCII text into a Unicode string"""
    def utf7_block(a):
        out = ''
        if a != '+':
            out = re.sub(r'[=\r\n]', '', basex.encode_base64(to_unicode(a, 'utf-16be')))
        return '+' + out + '-'
 
    if string is None:
        return ''
        
    if type == 'utf-16le':
        return struct.pack('<{}H'.format(len(string)), *struct.unpack('{}B'.format(len(string)), string))
    elif type == 'utf-16be':
        return struct.pack('>{}H'.format(len(string)), *struct.unpack('{}B'.format(len(string)), string))
    elif type == 'utf-32le':
        return struct.pack('<{}L'.format(len(string)), *struct.unpack('{}B'.format(len(string)), string))
    elif type == 'utf-32be':
        return struct.pack('>{}L'.format(len(string)), *struct.unpack('{}B'.format(len(string)), string))
    elif type == 'utf-7':
        if mode == 'all':
            return re.sub(r'.', lambda a: utf7_block(a.group()), string)
        else:
            return re.sub(r'[^\n\r\t\ A-Za-z0-9\'\(\),-.\/\:\?]', lambda a: utf7_block(a.group()), string)
    elif type == 'utf-8':
        if size == '':
            size = 2
            
        if size >= 2 and size <= 7:
            _string = ''
            for a in bytearray(string):
                if (a < 21 or a > 0x7f) or mode != '':
                    # try not to cringe
                    tmp = struct.pack('B', a)
                    bin = ''.join('{0:08b}'.format(ord(bites), 'b') for bites in tmp)
                    bin = list(bin)
                    bin = list(map(int, bin))
                    
                    out = [0] * (8 * size)
                    
                    for i in range(0, size):
                        out[i] = 1
                        out[i * 8] = 1
                        
                    i = 0
                    byte = 0
                    
                    for bit in reversed(bin):
                        while True:
                            if i < 6:
                                mod = (((size * 8) - 1) - byte * 8) - i
                                out[mod] = bit
                                i = i + 1
                            else:
                                byte = byte + 1
                                i = 0
                                continue
                            break
                            
                    if mode != '':
                        if mode == 'overlong':
                            pass
                        elif mode == 'invalid':
                            done = 0
                            while done == 0:
                                bits = [7, 8, 15, 16, 23, 24, 31, 32, 41]
                                for bit in bits:
                                    bit = (size * 8) - bit
                                    if bit > 1:
                                        _set = random.randrange(2)
                                        if out[bit] != _set:
                                            out[bit] = _set
                                            done = 1
                        else:
                            raise TypeError('Invalid mode.  Only "overlong" and "invalid" are accepted modes for utf-8')
                    newbin = ''.join(str(x) for x in out)
                    tmpint = int(newbin, 2)
                    tmpbytes = bytearray()
                    while tmpint:
                        tmpbytes.append(tmpint & 0xff)
                        tmpint >>= 8
                    _string += bytes(tmpbytes[::-1])
                else:
                    _string += struct.pack('B', a)
            return _string
        else:
            raise TypeError('invalid utf-8 size')