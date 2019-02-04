import conftest
from asaprog.pac_encoder import pac_encode
from asaprog.util import *

if __name__ == "__main__":
    pac = {
        'command': asaProgCommand.CHK_DEVICE.value,
        'data': b'test'
    }
    res = pac_encode(pac)
    print(res)
    print(res[-1])

