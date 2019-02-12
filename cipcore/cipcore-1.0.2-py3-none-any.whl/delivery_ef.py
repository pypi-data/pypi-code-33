import requests
import json
from ciperror import PublisherApiRequestError, EFResponseOfflineError


class DeliveryEfPublishRequestApi:
    """Send request"""
    def __init__(self, base_url=None, logger=None):
        self.base_url = f'{base_url}/api'
        self.logger = logger

    def _url(self, path):
        return self.base_url + path

    def send(self, body):
        try:
            url = self._url('/publish-request')
            self.logger.info(200, message=f'Enviando request de post Ef Delivery Service\
                API URL: {url} BODY: {json.dumps(body)}')
            response = requests.post(url, json=body)
        except Exception as ex:
            error = PublisherApiRequestError(str(ex))
            self.logger.error(error.code, error.http_status, message=error.message)
            raise error

        if response.status_code not in [200, 201, 204]:
            error = PublisherApiRequestError(response.text)
            self.logger.error(error.code, error.http_status, message=error.message)
            raise error

        return response

    def send_asset_id(self, asset_id):
        try:
            url = "/publish-request/{}".format(asset_id)
            url_ef = self._url(url)
            self.logger.info(200, message="Fazendo requisição de adição de profile ASSET ID: {}, URL: {}"
                         .format(asset_id, url_ef))
            response = requests.post(url_ef)

            if response.status_code in [200, 201, 204]:
               self.logger.info(200, message=f'Publish request feito com asset id: {asset_id}')
               return response

            if response.status_code == 409:
                self.logger.warning('', 409, message="Publish request já existe para este asset_id, retorno EF: {}"
                                .format(';'.join(response.json()['messages'])))
                return False

            ex = EFResponseOfflineError(str(response.content))
            self.logger.error(ex.code, 500, message=f'Erro ao enviar post para delivery ef service: {str(ex)}')
            raise ex
        except ConnectionError as ex:
            ex = EFResponseOfflineError(str(ex))
            self.logger.error(ex.code, 500, message=f'Erro ao enviar post para delivery ef service: {str(ex)}')
            raise ex

    def healthcheck(self):
        url = self._url('/healthcheck')
        try:
            response = requests.get(url, timeout=2)
            if response.ok:
                return True
            error = PublisherApiRequestError(response.text)
        except Exception as ex:
            error = PublisherApiRequestError(str(ex))
            
        self.logger.error(error.code, error.http_status, message=error.message)
            
        return False
