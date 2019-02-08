import os
import sys
import re
import inspect

## Adds / to the path.
folder2add = os.path.realpath(os.path.abspath(os.path.split(inspect.getfile( inspect.currentframe() ))[0]) + "//")
if folder2add not in sys.path:
    sys.path.insert(0, folder2add)

## Adds /disk_test to the path.
folder2add = os.path.realpath(os.path.abspath(os.path.split(inspect.getfile( inspect.currentframe() ))[0]) + "//disk_test")
if folder2add not in sys.path:
    sys.path.insert(0, folder2add)

## Adds /connection_specific to the path.
folder2add = os.path.realpath(os.path.abspath(os.path.split(inspect.getfile( inspect.currentframe() ))[0]) + "//connection_specific")
if folder2add not in sys.path:
    sys.path.insert(0, folder2add)

## Adds /device_specific to the path.
folder2add = os.path.realpath(os.path.abspath(os.path.split(inspect.getfile( inspect.currentframe() ))[0]) + "//device_specific")
if folder2add not in sys.path:
    sys.path.insert(0, folder2add)

## Adds /serial to the path.
folder2add = os.path.realpath(os.path.abspath(os.path.split(inspect.getfile( inspect.currentframe() ))[0]) + "//connection_specific//serial")
if folder2add not in sys.path:
    sys.path.insert(0, folder2add)

## Adds /QIS to the path.
folder2add = os.path.realpath(os.path.abspath(os.path.split(inspect.getfile( inspect.currentframe() ))[0]) + "//connection_specific//QIS")
if folder2add not in sys.path:
    sys.path.insert(0, folder2add)

## Adds /usb_libs to the path.
folder2add = os.path.realpath(os.path.abspath(os.path.split(inspect.getfile( inspect.currentframe() ))[0]) + "//connection_specific//usb_libs")
if folder2add not in sys.path:
    sys.path.insert(0, folder2add)

#importing a basic API  
from device import quarchDevice

from device_specific.quarchPPM import quarchPPM
from device_specific.quarchQPS import quarchQPS
from device_specific.quarchQPS import quarchStream
from device_specific.quarchArray import quarchArray
from device_specific.quarchArray import subDevice

from connection import startLocalQis, startLocalQps, closeQPS#, closeQIS

from connection_specific.connection_QIS import isQisRunning
from connection_specific.connection_QIS import QisInterface as qisInterface
from connection_specific.connection_QPS import isQpsRunning
from connection_specific.connection_QPS import QpsInterface as qpsInterface

from disk_test.ModuleSelection import GetQpsModuleSelection
from disk_test.IometerAutomation import generateIcfFromCsvLineData, readIcfCsvLineData, generateIcfFromConf, runIOMeter, processIometerInstResults, adjustTime
from disk_test.DiskTargetSelection import GetDiskTargetSelection
from FIO_interface import runFIO 

#importing debug functions
from Debug.ScanDevices import scanDevices
from Debug.versionCompare import requiredQuarchpyVersion