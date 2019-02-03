import progressbar
import serial
import time
from py_asa_loader import util


def parseIHex(filename):
    """parse a intel style hex to raw binary data"""
    data = b''
    with open(filename, 'r') as hexfile:
        try:
            for line in hexfile.readlines():
                if line == ':00000001FF\n':
                    return data
                elif line == ':00000001FF':
                    return data
                if line[0] != ':':
                    raise Exception("Invalid hexfile!", filename)
                dbg_bytes  = int(line[1:3], 16) # debug usage var
                dbg_addres = int(line[3:7], 16) # debug usage var
                dbg_type   = int(line[7:9], 16) # debug usage var
                data += bytearray.fromhex(line[9:-3])
                # print('byte:'+str(dbg_bytes)+' a:'+str(dbg_addres)+' t:'+str(dbg_type)+' d:'+line[9:-3])
                # print(bytearray.fromhex(line[9:-3]))
        finally:
            hexfile.close()

class Loader():
    def __init__(self, port, hexFilename):
        self.port = port

        data = parseIHex(hexFilename)
        self.dataSize = len(data)
        self.dataList = [data[i:i+256] for i in range(0, len(data), 256)]

        self.total_steps = len(self.dataList) + 2
        self.times = 1

        # program flash time in asa_m128
        self.magicalDelay = 0.03 
    
    def openComport(self):
        # 8,N,1 mode
        try:
            self.ser = serial.Serial(port=self.port, baudrate=115200, timeout=3)
        except serial.serialutil.SerialException:
            raise util.CantOpenComportException

    def cmdCheckIsAsaDevice(self):
        # The 'chk' packet is used to check the device is ASA series board.
        # If is, board will response 'ack' packet.
        chk = b'\xFC\xFC\xFC\xFA\x01\x00\x04\x74\x65\x73\x74\xC0'
        ack = b'\xFC\xFC\xFC\xFB\x01\x00\x04OK!!\xdc'
        self.ser.write(chk)
        get_data = self.ser.readline(len(chk))
        if get_data != ack:
            raise util.ChkDeviceException

    def cmdLoadData(self, data):
        packet  = b'\xFC\xFC\xFC\xFC\x01'
        packet += len(data).to_bytes(2, byteorder='big')
        packet += data
        packet += (sum(data)%256).to_bytes(1, byteorder='big')
        self.ser.write(packet)

    def cmdEnd(self):
        end = b'\xFC\xFC\xFC\xFC\x01\x00\x00\x00'
        ack = b'\xFC\xFC\xFC\xFD\x01\x00\x04OK!!\xdc'
        self.ser.write(end)
        get_data = self.ser.read(len(ack))
        if get_data != ack:
            raise util.EndingException
            

    def step(self):
        time.sleep(self.magicalDelay)

        if self.times == 1:
            self.openComport()
            self.cmdCheckIsAsaDevice()
        elif self.times == self.total_steps:
            self.cmdEnd()
        else:
            self.cmdLoadData(self.dataList[self.times-2])

        self.times = self.times + 1
