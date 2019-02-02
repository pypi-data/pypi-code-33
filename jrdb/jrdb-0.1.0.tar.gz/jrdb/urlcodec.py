import zlib

delimiter = ','
encoding = 'utf-8'


def encode(urls):
    return zlib.compress(delimiter.join(urls).encode(encoding))


def decode(data):
    return zlib.decompress(data).decode(encoding).split(delimiter)
