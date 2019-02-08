import time

try:
    from connection_specific.connection_USB import importUSB#, USBConn
except:
    print ("System Compatibility issue - Is your Python architecture consistent with the Operating System?")
    pass
from connection_specific.connection_Serial import serialList, serial


def scanDevices(target_conn = "all", debug = False):

    def list_serial():
        serial_ports = serialList.comports()
        serial_modules = []

        for i in serial_ports:
            try:
                ser = serial.Serial(i[0], 19200, timeout=1)
                ser.write(b'*serial?\r\n')
                time.sleep(2)
                s = ser.read(size = 64)
                serial_module = s.splitlines()[1]
            
                serial_module = str(serial_module)[1:].replace("'","")
            
                if "QTL" not in serial_module:
                    serial_module = "QTL" + serial_module
            
                module = str(i[0]), str(serial_module)

                if serial_module[7] == "-" and serial_module[10] == "-":
                    serial_modules.append(module)

                ser.close()
            except:
                pass
        return serial_modules

    def list_USB():

        def print_debug(debug_string):
            if debug:
                print (debug_string)
            else:
                 pass

        QUARCH_VENDOR_ID = 0x16d0
        QUARCH_PRODUCT_ID1 = 0x0449

        usb1 = importUSB()

        context = usb1.USBContext()
        usb_list = context.getDeviceList()

        print_debug(usb_list)

        usb_modules = []
            
        for i in usb_list:

            print_debug(i)

            if hex(i.device_descriptor.idVendor) == hex(QUARCH_VENDOR_ID) and hex(i.device_descriptor.idProduct) == hex(QUARCH_PRODUCT_ID1):
                try:
                    i_handle = i.open()
                except:
                    print ("Module busy! Error 10")
                    continue
                print_debug(i_handle)

                try:
                    module_sn = i_handle.getASCIIStringDescriptor(3)
                except:
                    print ("Module busy! Error 09")
                    continue

                try:
                    print_debug(i_handle.getASCIIStringDescriptor(3) +" "+ i_handle.getASCIIStringDescriptor(2) +" "+ i_handle.getASCIIStringDescriptor(1))
                except:
                    print ("Module busy! Error 11")
                    continue

                if "QTL" not in module_sn:
                    module_sn = "QTL" + module_sn
                
                try: 
                    module = str(i_handle._USBDeviceHandle__device).split(":")[0], str(module_sn.strip())
                except:
                    print ("Module busy! Error 12")
                    continue

                print_debug(module)
                
                usb_modules.append(module)
                
                try:
                    i_handle.close()
                except:
                    continue

        return usb_modules
    
    def list_network(target_conn):
        # Create and configure the socket for broadcast.
        mySocket = socket(AF_INET, SOCK_DGRAM)
        mySocket.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
        mySocket.settimeout(1)

        # Broadcast the message.
        mySocket.sendto(b'Discovery: Who is out there?\0\n',('255.255.255.255', 30303))
        
        telnet_modules = []
        rest_modules = []
    
        # Receive messages until timeout.
        while True:
            network_modules = {}

            # Receive raw message until timeout, then break.
            try:
                msg_received = mySocket.recvfrom(256)
            except:
                break
            cont = 0

            for lines in msg_received[0].splitlines():
                if cont <= 1:
                    index = cont
                    data = repr(lines).replace("'","").replace("b","")
                    cont += 1
                else:
                    index = repr(lines[0]).replace("'","")
                    data = repr(lines[1:]).replace("'","").replace("b","")

                network_modules[index] = data
                    
            # Filter the raw message to get the module and ip adress.
            module_name = network_modules.get(0).strip()
        
            ip_module = msg_received[1][0].strip()

            telnet_ip_list = []
            rest_ip_list = []
                
            try:
                # Add a QTL before modules without it.
                if "QTL" not in module_name.decode("utf-8"):
                    module_name = "QTL" + module_name.decode("utf-8")
            except:
                # Add a QTL before modules without it.
                if "QTL" not in module_name:
                    module_name = "QTL" + module_name
            
            # Checks if there's a value in the TELNET key.
            if network_modules.get("\\x8a") or network_modules.get("138"):
                ip_module_telnet = "TELNET:" + ip_module
                # Append the information to the list.
                module = ip_module_telnet, str(module_name)
                telnet_modules.append(module)
                del(module)
                del(ip_module_telnet)

            # Checks if there's a value in the REST key.
            if network_modules.get("\\x84") or network_modules.get("132"):
                ip_module_rest = "REST:" + ip_module
                # Append the information to the list.
                module = ip_module_rest, str(module_name)
                rest_modules.append(module)
                del(module)
                del(ip_module_rest)
                
        if target_conn.lower() == "rest":
            return rest_modules
        
        if target_conn.lower() == "telnet":
            return telnet_modules
    
    if target_conn.lower() == "all":
        return list_USB(), list_serial(), list_network("telnet"), list_network("rest")

    if target_conn.lower() == "serial":
        return list_serial()

    if target_conn.lower() == "usb":
        return list_USB()

    if target_conn.lower() == "rest" or target_conn.lower() == "telnet":
        return list_network(target_conn)