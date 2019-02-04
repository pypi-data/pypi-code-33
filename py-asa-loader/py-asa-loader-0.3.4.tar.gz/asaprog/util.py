import enum

HEADER = b'\xFC\xFC\xFC'
TOCKEN = b'\x01'

class asaProgCommand(enum.IntEnum):
    CHK_DEVICE = 0xFA
    ACK1 = 0xFB
    DATA = 0xFC
    ACK2 = 0xFD

PAC_CHK_DEVICE = {
    'command': asaProgCommand.CHK_DEVICE,
    'data': b'test'
}

PAC_ACK1 = {
    'command': asaProgCommand.ACK1,
    'data': b'OK!!'
}

PAC_END = {
    'command': asaProgCommand.DATA,
    'data': b''
}

PAC_ACK2 = {
    'command': asaProgCommand.ACK2,
    'data': b'OK!!'
}

class CantOpenComportException(Exception):
    pass

class ChkDeviceException(IOError):
    pass

class LoadDataException(IOError):
    pass

class EndingException(IOError):
    pass
