# coding: utf-8

from requests import Session
from zeep import Client
from zeep.transports import Transport


class PF(object):
    def __init__(self, cert_crt=None, cert_key=None, is_test=False):
        self.is_test = is_test
        self.cert_crt = cert_crt
        self.cert_key = cert_key

    def _client(self):
        session = Session()
        session.cert = (self.cert_crt, self.cert_key)
        transport = Transport(session=session)
        wsdl = 'https://pfront2.a-3.ru/ProcessingFront/ProcessingFrontWS?WSDL'
        if self.is_test:
            wsdl = 'https://devpfront2.a-3.ru/ProcessingFront/ProcessingFrontWS?WSDL'
        return Client(wsdl=wsdl, transport=transport)

    def client(self):
        return self._client()

    def WSDL(self):
        return self._client().wsdl

    def request(self, method, **args):
        # TODO: ...
        client = self._client()
        return client.create_message(client.service, method, **args)

    def initPayment(self, **args):
        """Method `initPayment`

        >>> .cancelPayment(systemID='EXAMPLE', orderID='560ce567-dd57-4d3b-a1b5-d358ce932810')
        """
        return self._client().service.initPayment(**args)

    def initAuthentication(self, **args):
        return self._client().service.initAuthentication(**args)

    def cancelPayment(self, **args):
        """Method `cancelPayment`

        >>> .cancelPayment(systemID='EXAMPLE', orderID='560ce567-dd57-4d3b-a1b5-d358ce932810')
        """
        return self._client().service.cancelPayment(**args)

    def enableRecurringKey(self, **args):
        """Method `enableRecurringKey`

        >>> .enableRecurringKey(systemID='EXAMPLE', key='1000000000', user={'phone': '9100000000'})
        {
            'code': 3,
            'description': 'Ключ не найден [key=1000000000].'
        }
        """
        return self._client().service.enableRecurringKey(**args)

    def getPaymentInfo(self, **args):
        """
        >>> .getPaymentInfo(**dict(systemID='EXAMPLE', orderID='38d2aefe-21ea-4e3b-91aa-05d9905f2d21'))
        {
            'operationResult': {
                'code': 1,
                'description': 'OK'
            },
            'orderID': '38d2aefe-21ea-4e3b-91aa-05d9905f2d21',
            'authCode': '111111',
            'terminal': '11111111',
            'cardNumber': '220000******0000',
            'bills': None,
            'trID': 1000000000
        }
        """
        return self._client().service.getPaymentInfo(**args)

    def getPaymentStatus(self, **args):
        """
        >>> .getPaymentStatus(**dict(systemID='EXAMPLE', orderID='38d2aefe-21ea-4e3b-91aa-05d9905f2d21'))
        {
            'operationResult': {
                'code': 1,
                'description': 'OK'
            },
            'orderStatus': {
                'orderID': '38d2aefe-21ea-4e3b-91aa-05d9905f2d21',
                'trStatus': '2',
                'trStatusDesc': None,
                'trChangeDateTime': None,
                'authCode': '111111',
                'terminal': '11111111',
                'cardNumber': '220000******0000',
                'trID': '1000000000'
            }
        }
        """
        return self._client().service.getPaymentStatus(**args)

    def dailyReportRequest(self, **args):
        """
        >>> .dailyReportRequest(systemID='EXAMPLE', date='2017-08-07', status=2, signature='')
        {
            'operationResult': {
                'code': 3,
                'description': 'Неверная подпись.'
            },
            'orders': None
        }
        """
        return self._client().service.dailyReport(**args)
