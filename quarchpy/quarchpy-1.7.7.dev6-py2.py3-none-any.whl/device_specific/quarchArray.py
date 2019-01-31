from device import quarchDevice

class quarchArray(quarchDevice):
    def __init__(self, originObj):
        self.originObj = originObj
        self.connectionObj = originObj.connectionObj
        self.ConType = originObj.ConType

    def getSubDevice(self, port):
        return subDevice(self.originObj, port)

class subDevice(quarchArray):

    def __init__(self, originObj, port):
        self.port = port
        self.originObj = originObj
        self.connectionObj = originObj.connectionObj
        self.ConType = originObj.ConType

    def sendCommand(self, CommandString):
        portNumb = str(self.port)
        return self.originObj.sendCommand(CommandString + " <" + portNumb + ">").replace("FPGA " +portNumb+ ":", "FPGA x:").replace(portNumb+":", "").replace(portNumb+".0:", "").replace("FPGA x:", "FPGA " +portNumb+ ":")