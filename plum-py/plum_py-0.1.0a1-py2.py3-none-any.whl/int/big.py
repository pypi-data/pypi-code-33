# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Copyright 2019 Daniel Mark Gass, see __about__.py for license information.
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

from ._int import Int

class SInt8(Int, nbytes=1, signed=True, byteorder='big'): pass
class SInt16(Int, nbytes=2, signed=True, byteorder='big'): pass
class SInt32(Int, nbytes=4, signed=True, byteorder='big'): pass
class SInt64(Int, nbytes=8, signed=True, byteorder='big'): pass

class UInt8(Int, nbytes=1, signed=False, byteorder='big'): pass
class UInt16(Int, nbytes=2, signed=False, byteorder='big'): pass
class UInt32(Int, nbytes=4, signed=False, byteorder='big'): pass
class UInt64(Int, nbytes=8, signed=False, byteorder='big'): pass

del Int
