import time
from core.internals.SignUtil import SignUtil


class SubDeviceLoginInfo(object):

    cleanSession = False

    def __init__(self, productKey, deviceKey, deviceSecret):
        self.productKey = productKey
        self.deviceKey = deviceKey
        self.clientId = self.getDefaultClientId(productKey, deviceKey)
        self.timestamp = int(time.time()*1000)
        self.signParams = dict()
        self.signParams['productKey'] = productKey
        self.signParams['deviceKey'] = deviceKey
        self.signParams['clientId'] = self.clientId
        self.signParams['timestamp'] = str(self.timestamp)

        self.sign = SignUtil.sign(deviceSecret, self.signParams)
        self.signMethod = SignUtil.hmacsha1
        self.signParams['signMethod'] = self.signMethod
        self.signParams['sign'] = self.sign
        self.signParams['cleanSession'] = str(self.cleanSession)

    def getSignParams(self):
        return self.signParams

    def getDefaultClientId(self, productKey, deviceKey):
        return productKey + deviceKey + str(int(time.time()*1000))

    def getProductKey(self):
        return self.productKey

    def getDeviceKey(self):
        return self.deviceKey