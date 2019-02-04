import requests
from ciperror import NotificationError, FTPServiceRequestError
from cip_workflow_status import WorkflowStep
from urllib.parse import urlparse
import os


class FTPService(object):

    def __init__(self, base_url=None, sftp_uri=None, logger=None):
        self.base_url = f'{base_url}/api'
        self.logger = logger
        self.sftp_uri = sftp_uri

    def _url(self, path):
        return self.base_url + path

    def send_file(self, delivery_job):

        url = self._url('/upload-file')

        try:
            json_body = self.create_json_body(delivery_job)
            self.logger.info(200, message="Chamando o FTP Service para fazer o upload do job: {}: URL: {} BODY: {}"
                             .format(delivery_job['id'], url, json_body))

            response = requests.post(url, json=json_body)
            if response.status_code in [200, 201, 204]:
                return True

        except KeyError as ex:
            ex = NotificationError(
                "ftp-service", "Erro ao chamar o ftp-service: " + str(ex))
            self.logger.error(code=ex.code, status=ex.http_status, message=ex.message)
            return False
        except Exception as ex:
            ex = NotificationError(
                "ftp-service", "Erro ao chamar o ftp-service: " + str(ex))
            self.logger.error(code=ex.code, status=ex.http_status, message=ex.message)
            return False

    def create_json_body(self, delivery_job):

        parsed_sftp_url = urlparse(self.sftp_uri)
        files_to_upload = []
        for file in delivery_job['files']:
            files_to_upload.append({
                "in": file['path'],
                "out": os.path.basename(file['path']),
                "status": ""
            })

        json_body = {
            "callback": self.base_url + '/api/tasks-responses',
            "body": {
                "delivery_job_id": delivery_job['id'],
                "ladder": delivery_job['ladder'],
                "step": WorkflowStep.DELIVERY_FILE_UPLOAD.to_string(),
                "host": parsed_sftp_url.hostname,
                "port": parsed_sftp_url.port,
                "user": parsed_sftp_url.username,
                "password": parsed_sftp_url.password,
                "files_to_upload": files_to_upload
            }
        }
        return json_body

    def healthcheck(self):
        url = self._url('/healthcheck')
        try:
            response = requests.get(url, timeout=2)
            if response.ok:
                return True
            error = FTPServiceRequestError(response.text)
        except Exception as ex:
            error = FTPServiceRequestError(str(ex))

        self.logger.error(error.code, error.http_status, message=error.message)

        return False

