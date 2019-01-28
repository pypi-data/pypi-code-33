class SDKConfig:
    """
    api 服务地址
    """
    API_SERVER = "http://dev-gateway.bdn-developer-alauda-qa.rootcloudapp.com"
    PUB_SUB_SERVER = "https://pubsub.rootcloud.com"
    TCP_PORT = 8007
    HTTP_PORT = 80

    """
    客户端id
    """
    CLIENT_ID = "clientId"

    """
    客户端秘钥
    """
    SECRET_KEY = "secret"

    """
    访问秘钥
    """
    ACCESS_TOKEN = "access.token"

    """
    客户端重连设置，
    默认重连
    """
    CLIENT_SDK_RECONNECT = "client.sdk.reconnect"

    """
    配置成功和失败
    """
    SUCCESS = True

    ERROR  =  "unauthorized"

    # api_server = "http://dev-gateway.bdn-developer-alauda-qa.rootcloudapp.com"

    #---------------------配置获取token的header头--------------#
    ACCEPT = "*/*"
    CONNE_CTION = "Keep-Alive"
    CONTENT_TYPE = "application/json"

    header = {
        "accept": ACCEPT,
        "connection": CONNE_CTION,
        "Content-Type": CONTENT_TYPE
    }

    LOGIN_URL = "/dev-auth/auth/pubSubAuth"




