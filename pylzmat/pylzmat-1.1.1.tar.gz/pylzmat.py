from _pylzmat import lib, ffi


def encode(data):
    size = len(data)
    outlen = (size) + ((size + 7) >> 3) + 0x21
    data_out = ffi.new("char[%d]" % outlen)
    data_out_buff = ffi.buffer(data_out)
    data_out_len = ffi.new("MP_U32 *")
    data_out_len[0] = outlen

    ret = lib.lzmat_encode(data_out, data_out_len, data, len(data))
    if ret == 0:
        return data_out_buff[:data_out_len[0]]
    else:
        raise Exception('Return error: %d' % ret)


def decode(data, size=None):
    if size:
        outlen = size

    else:
        outlen = len(data) * 100

    data_out = ffi.new("char[%d]" % outlen)
    data_out_buff = ffi.buffer(data_out)
    data_out_len = ffi.new("MP_U32 *")
    data_out_len[0] = outlen

    ret = lib.lzmat_decode(data_out, data_out_len, data, len(data))
    if ret == 0:
        return data_out_buff[:data_out_len[0]]
    else:
        raise Exception('Return error: %d' % ret)

