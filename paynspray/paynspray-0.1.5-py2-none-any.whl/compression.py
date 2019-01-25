import re, StringIO

try:
    import zlib
    zlib_present = True
except ImportError:
    zlib_present = False
    
try:
    import gzip as Gzip
    gzip_present = True
except ImportError:
    gzip_present = False
    

def compress(string):
    """Compresses a string by removing newline characters and extra whitespace"""
    if re.sub(r'\n', ' ', string) != string:
        string = re.sub(r'\n', ' ', string)
        
    if re.sub(r'\s+', ' ', string) != string:
        string = re.sub(r'\s+', ' ', string)
        
    if re.sub(r'^\s+', '', string) != string:
        string = re.sub(r'^\s+', '', string)
        
    if re.sub(r'\s+$', '', string) != string:
        string = re.sub(r'\s+$', '', string)
        
    return string
    
def zlib_deflate(string, level = zlib.Z_BEST_COMPRESSION):
    """Compresses a buffer using Zlib"""
    if zlib_present == True:
        zstream = zlib.compressobj(level)
        buf = zstream.compress(string)
        buf += zstream.flush(zlib.Z_FINISH)
        return buf
    else:
        raise RuntimeError("Zlib support is not present.")
        
def zlib_inflate(string):
    """Decompresses a buffer using Zlib"""
    if zlib_present == True:
        zstream = zlib.decompressobj()
        buf = zstream.decompress(string)
        buf += zstream.flush()
        return buf
    else:
        raise RuntimeError("Zlib support is not present.")
        
def gzip(string, level = 9):
    """Compresses a buffer using Gzip"""
    if gzip_present == False:
        raise RuntimeError("Gzip support is not present.")
        
    if (level < 1 or level > 9):
        raise RuntimeError("Invalid Gzip compression level")
        
    s = StringIO.StringIO("")
    
    gz = Gzip.GzipFile(filename = None, mode = 'wb', compresslevel = level, fileobj = s)
    gz.write(string)
    gz.close()
    
    return s.getvalue()
    
def ungzip(string):
    """Decompresses a buffer using Gzip"""
    if gzip_present == False:
        raise RuntimeError("Gzip support is not present.")
        
    s = ""
    if hasattr(s, "encode") == True:
        s.encode('ascii', 'ignore')
        
    gz = Gzip.GzipFile(filename = None, mode = 'rb', fileobj = StringIO.StringIO(string))
    s += gz.read()
    gz.close()
    return s