"""
*User: JiltFly
*Date: 2018 / 12 / 4
*Time: 14:25
*email: it.shuaifei@gmail.com
*This is the configuration center
"""
import os
class Config:
    #------------------- start -------------------#

    #This is realm name
    # url = "*********************"

    #This is your App Code
    # appCode = "***********************"

    #This is your accessSecret
    # secret = "*****************"

    #This is request API Token  URL
    apiUrl = "/dev-auth/auth/clientAuth"

    #This is the information with which the request is generic
    accept = "*/*"
    connection = "Keep-Alive"
    contentType = "application/json"

    #Information sent with an expired identity
    message = 'iot.auth.Expired'
    mess    = 'iot.auth.AuthenticationFailed'

    success = "success"
    iootech = "IrootechAuth"

    #Files that store tokens and get the current time of tokens
    # path      = os.getcwd()+"\\developer_python_sdk_api\src\\token.py"
    path       = os.path.abspath(os.path.dirname(os.path.abspath(__file__)) + os.path.sep + ".")+"\\token.py"
    #The time when the identity expires 24 hours
    timeToken = 24*60*60

    irootechAuth = ""

    #This is the header information for the request
    headers = {
        "accept": accept,
        "connection": connection,
        "Content-Type":contentType,
    }

    # allocation = {
    #     "clientId": appCode,
    #     "secret"  : secret
    #     }