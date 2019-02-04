from asaprog.util import *
from asaprog.pac_decoder import PacketDecoder
from asaprog.pac_encoder import pac_encode

import progressbar
import argparse
import serial
import time

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
                dbg_bytes = int(line[1:3], 16)  # debug usage var
                dbg_addres = int(line[3:7], 16)  # debug usage var
                dbg_type = int(line[7:9], 16)  # debug usage var
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

    def _openComport(self):
        # 8,N,1 mode
        try:
            self.ser = serial.Serial(
                port=self.port, baudrate=115200, timeout=3)
        except serial.serialutil.SerialException:
            raise CantOpenComportException

    def cmdCheckIsAsaDevice(self):
        # The 'PAC_CHK_DEVICE' packet is used to check the device is ASA series board.
        # If is, board will response 'PAC_ACK1' packet.
        req = pac_encode(PAC_CHK_DEVICE)
        rep = pac_encode(PAC_ACK1)
        self.ser.write(req)
        get_data = self.ser.read(len(rep))
        if get_data != rep:
            raise ChkDeviceException

    def cmdLoadData(self, data):
        pac = {
            'command': asaProgCommand.DATA,
            'data': data
        }
        req = pac_encode(pac)
        self.ser.write(req)

    def cmdEnd(self):
        # The 'PAC_CHK_DEVICE' packet is used to end the comunication.
        # If is, board will response 'PAC_ACK2' packet.
        req = pac_encode(PAC_END)
        rep = pac_encode(PAC_ACK2)
        self.ser.write(req)
        get_data = self.ser.readline(len(rep))
        if get_data != rep:
            raise EndingException

    def step(self):
        time.sleep(self.magicalDelay)

        if self.times == 1:
            self._openComport()
            self.cmdCheckIsAsaDevice()
        elif self.times == self.total_steps:
            self.cmdEnd()
        else:
            self.cmdLoadData(self.dataList[self.times-2])

        self.times = self.times + 1

## CLI tool
def argHandler():
    parser = argparse.ArgumentParser(
        description='Load program to ASA series board.')
    parser.add_argument('-H', '--hex',
                        dest='hexfile', action='store', type=str,
                        help='assign hex file to be load')
    parser.add_argument('-p', '--port',
                        dest='port', action='store', type=str,
                        help='assign the port to load')
    args = parser.parse_args()
    return args

def run():
    args = argHandler()

    loader = Loader(args.port, args.hexfile)
    print('program size: {:0.2f} KB'.format(loader.dataSize))

    widgets = [
        ' [', progressbar.Timer(), '] ',
        progressbar.Bar(),
        progressbar.Counter(format='%(percentage)0.2f%%'),
    ]
    bar = progressbar.ProgressBar(
        max_value=loader.total_steps, widgets=widgets)
    bar.update(0)

    for i in range(loader.total_steps):
        try:
            loader.step()
            bar.update(i)
        except ChkDeviceException as e:
            bar.finish(end='\n', dirty=True)
            print('Error: The device is not asa-board.')
        except CantOpenComportException as e:
            bar.finish(end='\n', dirty=True)
            print('Error: Cannot open the comport \'{}\'.'.format(loader.port))
            print(
                '    Please check the arg port is right and the comport is not in used.')
            print('    The arg \'port\' shoule be like \'COM1\', \'COM2\'...')
            break
        except EndingException as e:
            bar.finish(end='\n', dirty=True)
            print('Error: The device ignored the ending command .')
            break

if __name__ == '__main__':
    run()
