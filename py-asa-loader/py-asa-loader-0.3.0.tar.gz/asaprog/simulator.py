from asaprog.pac_decoder import PacketDecoder
from asaprog.pac_encoder import pac_encode
from asaprog.util import *

import time
import serial
import argparse

class Simulator(object):
    def __init__(self, port):
        super(Simulator, self).__init__()
        self.pd = PacketDecoder()
        self.ser = serial.Serial(
            port=port,
            baudrate=115200,
            timeout=1
        )

    def run(self):
        while self.ser.isOpen():
            ch = self.ser.read(1)
            if ch == b'':
                continue
            self.pd.step(ch[0])
            if self.pd.isDone():
                pac = self.pd.getPacket()
                print('cmd:{}, data_len:{}'.format(pac['command'], len(pac['data'])))
                if pac['command'] is asaProgCommand.CHK_DEVICE:
                    rep = pac_encode(PAC_ACK1)
                    self.ser.write(rep)
                    print('CHK_DEVICE rep:{}'.format(rep))
                elif pac['command'] is asaProgCommand.DATA and len(pac['data']) == 0:
                    rep = pac_encode(PAC_ACK2)
                    self.ser.write(rep)
                    print('END rep:{}'.format(rep))

## CLI tool
def argHandler():
    parser = argparse.ArgumentParser(
        description='Simulate a asa device to test asaloader.')
    parser.add_argument('-p', '--port',
                        dest='port', action='store', type=str,
                        help='assign the port to simulate')
    args = parser.parse_args()
    return args

def run():
    args = argHandler()
    simulator = Simulator(args.port)
    simulator.run()

if __name__ == '__main__':
    run()
