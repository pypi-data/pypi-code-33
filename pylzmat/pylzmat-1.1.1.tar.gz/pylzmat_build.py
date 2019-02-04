from cffi import FFI

ffibuilder = FFI()

source = """
typedef unsigned char   MP_U8;
typedef unsigned int    MP_U32;
int lzmat_encode(MP_U8 *pbOut, MP_U32 *pcbOut, MP_U8 *pbIn, MP_U32 cbIn);
int lzmat_decode(MP_U8 *pbOut, MP_U32 *pcbOut, MP_U8 *pbIn, MP_U32 cbIn);
"""
ffibuilder.set_source(
    "_pylzmat",  # name of the output C extension
    """#include "lzmat.h" """,
    sources=['src/lzmat/lzmat_enc.c', 'src/lzmat/lzmat_dec.c'],   # includes pi.c as additional sources
    include_dirs=['src/lzmat']

)

# ffibuilder.cdef("int lzmat_encode(char *pbOut, int *pcbOut, char *pbIn, int cbIn);")
# ffibuilder.cdef("int lzmat_decode(char *pbOut, int *pcbOut, char *pbIn, int cbIn);")

ffibuilder.cdef(source)

if __name__ == "__main__":
    ffibuilder.compile(verbose=True)
