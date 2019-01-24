# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

DTYPE_1ST = 0 << 6
DTYPE_2ND = 1 << 6
DTYPE_EXT = 2 << 6
DTYPE_EXDA= 3 << 6
MSK_DTYPE = 0xC0

EXT_TYPE_SYNCFINISH = 0x1f
EXT_TYPE_ACK = 0x00
EXT_TYPE_NACK = 0x01
MSK_EXT_DTYPE = 0x3f

class SensorManager:
    def __init__(self):
        self.readState = 0
        self.sensorValue = [-1] * 11;
        self.sensorID = [-1] * 8;
        self.statWrite = 0    # 0: none 1: waiting -1: NACK
        self.statSyncServo = 0

    def parseData(self, data):
        for i in range(0, len(data)):
            if (data[i] & MSK_DTYPE) == DTYPE_1ST:
                if not self.readState == 0:
                    continue
                self.data1 = data[i]
                self.readState = 1
            elif (data[i] & MSK_DTYPE) == DTYPE_2ND:
                if not self.readState == 1:
                    continue
                self.data2 = data[i]
                port = (self.data1 >> 2) & 0x0f
                if self.sensorID[port] == 0 or self.sensorID[port] == 1:
                    val = ((self.data1 & 0x03) << 6) | (self.data2 & 0x3f)
                    self.sensorValue[port] = val
                    self.readState = 0
                else:
                    self.readState = 2
                #print('sensor update')
            elif (data[i] & MSK_DTYPE) == DTYPE_EXDA:
                if not self.readState == 2:
                    continue
                port = (self.data1 >> 2) & 0x0f
                if self.sensorID[port] == 6:
      	            val = ((self.data1 & 0x03) << 6) | ((self.data2 & 0x3f)) | ((data[i] & 0x03)<< 8)
                else:
                    val = -1
                self.sensorValue[port] = val
                self.readState = 0
            elif (data[i] & MSK_DTYPE) == DTYPE_EXT:
                if data[i] & MSK_EXT_DTYPE == EXT_TYPE_SYNCFINISH:
                    #print('sync stop')
                    self.statSyncServo = 0
                if data[i] & MSK_EXT_DTYPE == EXT_TYPE_ACK:
                    #print('ACK received.')
                    self.statWrite = 0
                if data[i] & MSK_EXT_DTYPE == EXT_TYPE_NACK:
                    self.statWrite = -1

    def getValue(self, index):
        return self.sensorValue[index]

    def startWaitingWriteResponse(self):
        self.statWrite = 1

    def getWriteFlag(self):
        return self.statWrite

    def startSyncServo(self):
        self.statSyncServo = 1

    def getSyncServoFlag(self):
        return self.statSyncServo

    def registerSensorType(self, index, snstype):
        self.sensorID[index] = snstype
