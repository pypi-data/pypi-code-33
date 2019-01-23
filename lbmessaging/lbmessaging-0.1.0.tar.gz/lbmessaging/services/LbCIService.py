from lbmessaging.services.Common import BaseService


class LbCIService(BaseService):
    """
    LHCb continuous integration messaging service
    The exposed exchanges and their methods are:

        - send_build_ready      mapped to send_build_ready of
                                ContinuousIntegrationExchange
        - consume_build_ready   mapped to consume_build_ready of
                                ContinuousIntegrationExchange

    """
    def __init__(self, host=None, username=None, passwd=None, port=5671,
                 vhost='/lhcb', use_ssl=True):
        """
        :param host: the RabbitMQ server hostname
        :param username: the RabbitMQ server username
        :param passwd: the RabbitMQ server password
        :param port: the RabbitMQ server port
        :param vhost: the RabbitMQ virtual host that should be used in the
                      connection
        :param use_ssl: if True, an encrypted connection is created, plain text
                        otherwise
        """
        super(LbCIService, self).__init__(host=host, username=username,
                                          passwd=passwd, port=port,
                                          vhost=vhost, use_ssl=use_ssl)
