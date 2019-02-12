__version__ = '0.1.0'

try:
    from .rfid import RFID
    from .util import RFIDUtil
except RuntimeError:
    print("Must be used on Raspberry Pi")
