import time
from core.internals.SignUtil import SignUtil
from concurrent.futures import ThreadPoolExecutor


class Profile(object):

    VERSION = "1.0"
    MQTTv3_1 = 3
    MQTTv3_1_1 = 4
    DEFAULT_KEEP_ALIVE_INTERVAL = 60
    DEFAULT_CONNECTION_TIMEOUT = 30
    DEFAULT_OPERATION_TIMEOUT = 60
    regionURL = ''
    productKey = ''
    deviceKey = ''
    deviceSecret = ''
    keepAlive = DEFAULT_KEEP_ALIVE_INTERVAL
    connectionTimeout = DEFAULT_CONNECTION_TIMEOUT
    timeToWait = DEFAULT_OPERATION_TIMEOUT
    timestamp = int(time.time() * 1000)
    sslSecured = False
    sslJksPath = ''
    sslAlgorithm = 'SunX509'
    sslPassword = ''
    sslRootCAPath = ''
    sslPrivateKeyPath = ''
    sslPrivateKeyPass = None
    sslCertificatePath = ''
    useWebSocket = False

    def __init__(self,regionUrl,productKey,deviceKey,deviceSceret):
        self.regionURL = regionUrl
        self.productKey = productKey
        self.deviceKey = deviceKey
        self.deviceSecret = deviceSceret
        self.keepAlive = self.DEFAULT_KEEP_ALIVE_INTERVAL
        self.connectionTimeout = self.DEFAULT_CONNECTION_TIMEOUT
        self.timeToWait = self.DEFAULT_OPERATION_TIMEOUT
        self.executor = ThreadPoolExecutor(20, 'command-pool-')

    def getRegionURL(self):
        return self.regionURL

    def getProductKey(self):
        return self.productKey

    def getDeviceKey(self):
        return self.deviceKey

    def getDeviceSecret(self):
        return self.deviceSecret

    def getKeepAlive(self):
        return self.keepAlive

    def setKeepAlive(self, keepAlive):
        self.keepAlive = keepAlive
        return self

    def getConnectionTimeout(self):
        return self.connectionTimeout

    def setConnectionTimeout(self, connectionTimeout):
        self.connectionTimeout = connectionTimeout
        return self

    def getTimeToWait(self):
        return self.timeToWait

    def setTimeToWait(self, timeToWait):
        self.timeToWait = timeToWait
        return self

    def getClientId(self):
        return self.deviceKey + '|securemode=2,signmethod=' + SignUtil.hmacsha1 \
               + ',timestamp=' + str(self.timestamp) + '|'

    def getSSLSecured(self):
        return self.sslSecured

    def setSSLSecured(self, sslSecured):
        self.sslSecured = sslSecured
        return self

    def setSSLJksPath(self, sslJksPath, sslPassword):
        self.sslJksPath = sslJksPath
        self.sslPassword = sslPassword
        return self

    def setSSLAlgorithm(self, sslAlgorithm):
        self.sslAlgorithm = sslAlgorithm
        return self

    def getSSLRootCAPath(self):
        return self.sslRootCAPath

    def setSSLRootCAPath(self, sslRootCAPath):
        self.sslRootCAPath = sslRootCAPath
        return self

    def getSSLPrivateKeyPath(self):
        return self.sslPrivateKeyPath

    def setSSLPrivateKeyPath(self, sslPrivateKeyPath):
        self.sslPrivateKeyPath = sslPrivateKeyPath
        return self

    def getSSLCertificatePath(self):
        return self.sslCertificatePath

    def setSSLCertificatePath(self, sslCertificatePath):
        self.sslCertificatePath = sslCertificatePath
        return self

    def getSSLPrivateKeyPass(self):
        return self.sslPrivateKeyPass

    def setSSLPrivateKeyPass(self, sslPrivateKeyPass):
        self.sslPrivateKeyPass = sslPrivateKeyPass
        return self

    def setSSLContext(self, sslRootCAPath, sslCertificatePath, sslPrivateKeyPath, sslPrivateKeyPass = None):
        self.sslRootCAPath = sslRootCAPath
        self.sslCertificatePath = sslCertificatePath
        self.sslPrivateKeyPath = sslPrivateKeyPath
        self.sslPrivateKeyPass = sslPrivateKeyPass
        self.sslSecured = True
        return self

    def getMqttUser(self):
        return self.deviceKey + '&' + self.productKey

    def getMqttPassword(self):
        params = dict()
        params['productKey'] = self.getProductKey()
        params['deviceKey'] = self.getDeviceKey()
        params['clientId'] = self.getDeviceKey()
        params['timestamp'] = str(self.timestamp)

        return SignUtil.sign(self.getDeviceSecret(), params)

    def getUseWebSocket(self):
        return self.useWebSocket

    def setUseWebSocket(self, useWebSocket):
        self.useWebSocket = useWebSocket

    def getExecutor(self):
        return self.executor