import os, sys 
import inspect 
import time, platform 
from connection_QIS import QisInterface, isQisRunning 
from connection_QPS import QpsInterface, isQpsRunning 
import subprocess 
 
def blockPrint(): 
    sys.stdout = open(os.devnull, 'w') 
 
def enablePrint(): 
    sys.stdout = sys.__stdout__ 
 
def startLocalQis(QisPath=None): 
 
 
    blockPrint() 
 
    if QisPath == None: 
        QisPath = os.path.join(os.path.abspath(__file__), "..", "connection_specific", "QIS", "qis.jar") 

    #find file path and change directory to Qis Location 
    filepath = os.path.dirname(__file__)
    current_direc = os.getcwd() 
    os.chdir(filepath + "/connection_specific/QIS")     
    command = "-jar \"" + filepath + "/connection_specific/QIS/qis.jar\"" 


    #different start for different OS 
    currentOs = platform.system()  
    if (currentOs == "Windows"): 
        command = "start /high /b javaw " + command 
        os.system(command) 
    elif (currentOs == "Linux"):
        if sys.version_info[0] < 3:
            os.popen2("java " + command)
        else:
            os.popen("java " + command)
    else: 
        command = "start /high /b javaw " + command 
        os.system(command)

    #Qis needs a small time for startup
    time.sleep(2)

    #see if new instance of qis has started
    while not isQisRunning(runNewScan = False):
        time.sleep(0.1)
        pass
    
    #change directory back to start directory 
    os.chdir(current_direc) 
    
    try: 
        startLocalQis.func_code = (lambda:None).func_code 
    except: 
        startLocalQis.__code__ = (lambda:None).__code__  
     
    enablePrint()

def closeQIS(host='127.0.0.1', port=9722):
    myQis = QisInterface(host, port)
    myQis.sendAndReceiveCmd(cmd = "$shutdown")
    del myQis

def startLocalQps(QpsPath=None, keepQisRunning=False):
    
    if keepQisRunning:
        if not isQisRunning():
            startLocalQis()
    
    blockPrint()

    filepath = os.path.dirname(__file__)
    
    current_direc = os.getcwd()
    
    os.chdir(filepath + "/connection_specific/QPS")
    
    command = "-jar \"" + filepath + "/connection_specific/QPS/qps.jar\""    
    
    currentOs = platform.system() 
    
    if (currentOs is "Windows"):
        command = "start /high /b javaw -Djava.awt.headless=true " + command
        os.system(command)
    elif (currentOs in "Linux"):
        if sys.version_info[0] < 3:
            os.popen2("java " + command + " 2>&1")
        else:
            os.popen("java " + command + " 2>&1")
    else:
        command = "start /high /b javaw -Djava.awt.headless=true " + command
        os.system(command)
     
    
    while not isQpsRunning():
        time.sleep(0.1)
        pass
    
    os.chdir(current_direc)

    enablePrint()    
 
def closeQPS(host='127.0.0.1', port=9822): 
    myQps = QpsInterface(host, port) 
    myQps.sendCmdVerbose("$shutdown") 
    del myQps 
 
 
 
class QISConnection: 
     
    def __init__(self, ConString, host, port): 
        self.qis = QisInterface(host, port)     # Create an instance of QisInterface. Before this is ran QIS needs to have been started 
 
 
class PYConnection: 
     
    def __init__(self, ConString): 
        # Finds the separator. 
        Pos = ConString.find (':') 
        if Pos is -1: 
            raise ValueError ('Please check your module name!') 
        # Get the connection type and target. 
        self.ConnTypeStr = ConString[0:Pos] 
        self.ConnTarget = ConString[(Pos+1):] 

        if self.ConnTypeStr.lower() == 'rest': 
            from connection_ReST import ReSTConn 
            if "qtl" in self.ConnTarget.lower():
                self.ConnTarget.replace("qtl","")
            self.connection = ReSTConn(self.ConnTarget) 
             
        elif self.ConnTypeStr.lower() == 'usb': 
            from connection_specific.connection_USB import USBConn
            self.connection = USBConn(self.ConnTarget) 
         
        elif self.ConnTypeStr.lower() == 'serial': 
            from connection_Serial import SerialConn 
            self.connection = SerialConn(self.ConnTarget) 
         
        elif self.ConnTypeStr.lower() == 'telnet': 
            from connection_Telnet import TelnetConn 
            self.connection = TelnetConn(self.ConnTarget) 
         
        else: 
            raise ValueError ("Invalid connection type in module string!")  
 
 
class QPSConnection: 
 
    def __init__(self, host, port): 
        self.qps = QpsInterface(host, port)