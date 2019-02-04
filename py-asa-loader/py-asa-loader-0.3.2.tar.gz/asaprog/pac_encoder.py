from asaprog.util import *
import enum

def pac_encode(pac):
    chksum = sum(pac['data']) %256

    res = bytes()
    res += HEADER
    res += bytes([pac['command']])
    res += TOCKEN
    res += len(pac['data']).to_bytes(2,'big')
    res += pac['data']
    res += chksum.to_bytes(1,'big')
    return res
