import conftest
from asaprog.pac_decoder import PacketDecoder

if __name__ == "__main__":
    pd = PacketDecoder()
    data = b'\xFC\xFC\xFC\xFA\x01\x00\x04\x74\x65\x73\x74\xC0'
    for ch in data:
        pd.step(ch)
        if pd.isDone():
            print(pd.getPacket())
