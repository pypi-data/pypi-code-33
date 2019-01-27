#!/usr/bin/env python
import sys, struct, array, fcntl, time
import bluetooth
import bluetooth._bluetooth as bt
#from bluetooth.ble import DiscoveryService

class BTSocket(object):
    def __init__(self, addr):
        self.addr = addr
        self.hci_sock = bt.hci_open_dev()
        self.hci_fd = self.hci_sock.fileno()
        self.bt_sock = bluetooth.BluetoothSocket(bluetooth.L2CAP)
        self.bt_sock.settimeout(None)
        self.connected = False
        self.cmd_pkt = None 
        self.keepalive = True
        self.ble_discovery = DiscoveryService()

    def set_cmd_pkt(self):
        # This is a hack to get this working in python2 and python3
        if sys.version_info[0] >= 3:
            reqstr = struct.pack(
                "6sB17s", 
                bt.str2ba(self.addr),
                bt.ACL_LINK,
                bytearray(17))
            request = array.array("b", reqstr)
        else:
            reqstr = struct.pack(
                "6sB17s", 
                bt.str2ba(self.addr),
                bt.ACL_LINK,
                "\0" * 17)
            request = array.array("c", reqstr)
        handle = fcntl.ioctl(self.hci_fd, bt.HCIGETCONNINFO, request, 1)
        handle = struct.unpack("8xH14x", request.tostring())[0]
        self.cmd_pkt = struct.pack('H', handle)

    def connect(self):
        self.bt_sock.connect_ex((self.addr, 1)) # PSM 1 - Service Discovery
        self.connected = True

#    def ble_discovery_scan(self):
#        devices = this.ble_discovery.discover(2)
#        return devices.items()

    def get_rssi(self):
        try:
            if not self.connected:
                self.connect()
            if self.cmd_pkt is None:
                self.set_cmd_pkt()
            rssi = bt.hci_send_req(
                    self.hci_sock,
                    bt.OGF_STATUS_PARAM,
                    bt.OCF_READ_RSSI,
                    bt.EVT_CMD_COMPLETE,
                    4,
                    self.cmd_pkt)

            if self.keepalive:
                self.bt_sock.send("ping")

            # Another hacky python2/3 fix
            if sys.version_info[0] >= 3:
                return struct.unpack('b', rssi[3].to_bytes(1, 'big'))[0]
            else:
                return struct.unpack('b', rssi[3])[0]
        except IOError:
            self.connected = False
            return None

if __name__ == "__main__":
    btsock = BTSocket(sys.argv[1])
    while(True):
        print(btsock.get_rssi())
        btsock.bt_sock.send("ping")
        time.sleep(1)
