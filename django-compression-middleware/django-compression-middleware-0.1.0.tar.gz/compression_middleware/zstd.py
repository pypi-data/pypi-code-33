# -*- encoding: utf-8 -*-
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

__all__ = ['zstd_compress', 'zstd_compress_stream']


from django.utils.text import StreamingBuffer

import zstandard as zstd


DEFAULT_LEVEL = 3
DEFAULT_LEVEL = 7


#TODO: store cctx in thread local variable
#from threading import local
#_local = local()
# def get_ctx():
#     if 'ctx' not in _local.__dict__:
#         _local.ctx = zstd.ZstdCompressor(level=DEFAULT_LEVEL)
#     return _local.ctx


def zstd_compress(content):
    cctx = zstd.ZstdCompressor(level=DEFAULT_LEVEL)
    return cctx.compress(content)


def zstd_compress_stream(sequence):
    buf = StreamingBuffer()
    cctx = zstd.ZstdCompressor(level=DEFAULT_LEVEL)
    with cctx.stream_writer(buf) as compressor:
        yield buf.read()
        for item in sequence:
            if compressor.write(item):
                yield buf.read()
    yield buf.read()


def __zstd_compress_stream(sequence):
    # Output headers immediately, so that we can package the rest up in chunks
    # the size of a likely MTU. The headers are of unknown size, so if that is
    # out of the way, we can do our best with the response body.
    yield b''

    cctx = zstd.ZstdCompressor(level=DEFAULT_LEVEL)
    chunker = cctx.chunker(chunk_size=1420)
    for item in sequence:
        for out_chunk in chunker.compress(item):
            yield out_chunk

    for out_chunk in chunker.finish():
        yield out_chunk
