import time
from core.internals.SignUtil import SignUtil


class SubDeviceInfo(object):

    def __init__(self, productKey, deviceKey, deviceSecret):
        self.productKey = productKey
        self.deviceKey = deviceKey
        self.clientId = self.getDefaultClientId(productKey, deviceKey)
        self.timestamp = int(time.time()*1000)
        self.signMethod = SignUtil.hmacsha1
        self.deviceSecret = deviceSecret
        signParams = dict()
        signParams['productKey'] = productKey
        signParams['deviceKey'] = deviceKey
        signParams['clientId'] = self.clientId
        signParams['timestamp'] = str(self.timestamp)
        self.sign = SignUtil.sign(deviceSecret, signParams)

    def getDefaultClientId(self, productKey, deviceKey):
        return "{}.{}.{}".format(productKey, deviceKey, str(int(time.time()*1000)))

    def getClientId(self):
        return self.clientId

    def setClientId(self, clientId):
        self.clientId = clientId

    def getTimestamp(self):
        return self.timestamp

    def setTimestamp(self, timestamp):
        self.timestamp = timestamp

    def getSignMethod(self):
        return self.signMethod

    def setSignMethod(self, signMethod):
        self.signMethod = signMethod

    def getSign(self):
        return self.sign

    def setSign(self, sign):
        self.sign = sign

    def createSignMap(self):
        params = dict()
        params['productKey'] = self.productKey
        params['deviceKey'] = self.deviceKey
        params['clientId'] = self.clientId
        params['timestamp'] = str(self.timestamp)
        params['signMethod'] = self.signMethod
        params['sign'] = self.sign
        return params

    def getProductKey(self):
        return self.productKey

    def getDeviceKey(self):
        return self.deviceKey

    def setProductKey(self, productKey):
        self.productKey = productKey
        return self

    def setDeviceKey(self, deviceKey):
        self.deviceKey = deviceKey
        return self