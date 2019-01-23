import requests


class ClientResponse:
    def __init__(self, status, msg, result):
        self.status = status
        self.msg = msg
        self.result = result


class HttpException(Exception):
    def __init__(self, status_code):
        self.status_code = status_code


class Client:
    API_HOST = 'https://api.openload.co/1'
    ACCOUNT_INFO_URI = '/account/info'
    DOWNLOAD_TICKET_URI = '/file/dlticket'
    DOWNLOAD_LINK_URI = '/file/dl'
    FILE_INFO_URI = '/file/info'
    UPLOAD_URI = '/file/ul'
    ADD_REMOTE_UPLOAD_URI = '/remotedl/add'
    REMOTE_UPLOAD_STATUS_URI = '/remotedl/status'
    LIST_FOLDER_URI = '/file/listfolder'
    RENAME_FOLDER_URI = '/file/renamefolder'
    RENAME_FILE_URI = '/file/rename'
    DELETE_FILE_URI = '/file/delete'
    CONVERT_FILE_URI = '/file/convert'
    RUNNING_CONVERTS_URI = '/file/runningconverts'
    GET_SPLASH_IMAGE_URI = '/file/getsplash'

    def __init__(self, login=None, key=None):
        self.login = login
        self.key = key

    def account_info(self):
        return self.__req(self.ACCOUNT_INFO_URI)

    def download_ticket(self, filename):
        params = {
            'file': filename,
        }
        return self.__req(self.DOWNLOAD_TICKET_URI, params=params)

    def download_link(self, filename, ticket, captcha):
        params = {
            'file': filename,
            'ticket': ticket,
            'captcha_response': captcha,
        }
        return self.__req(self.DOWNLOAD_LINK_URI, params=params)

    def file_info(self, filename):
        params = {
            'file': filename,
        }
        return self.__req(self.FILE_INFO_URI, params=params)

    def upload(self, folder=None, sha1=None, httponly=None):
        params = []
        if folder is not None:
            params['folder'] = folder
        if sha1 is not None:
            params['sha1'] = sha1
        if httponly is not None:
            params['httponly'] = httponly
        return self.__req(self.UPLOAD_URI, params=params)

    def add_remote_upload(self, url, folder=None, headers=None):
        params = {
            'url': url,
        }
        if folder is not None:
            params['folder'] = folder
        if headers is not None:
            params['headers'] = '\n'.join(['{}: {}'.format(k, v) for k, v in headers.iteritems()])
        return self.__req(self.ADD_REMOTE_UPLOAD_URI, params=params)

    def remote_upload_status(self, limit=None, upload_id=None):
        params = {}
        if limit is not None:
            params['limit'] = limit
        if upload_id is not None:
            params['id'] = upload_id
        return self.__req(self.REMOTE_UPLOAD_STATUS_URI, params=params)

    def list_folder(self, folder=None):
        params = []
        if folder is not None:
            params['folder'] = folder
        return self.__req(self.LIST_FOLDER_URI, params=params)

    def rename_folder(self, folder, new_name):
        params = {
            'folder': folder,
            'name': new_name,
        }
        return self.__req(self.RENAME_FOLDER_URI, params=params)

    def rename_file(self, filename, new_name):
        params = {
            'file': filename,
            'name': new_name,
        }
        return self.__req(self.RENAME_FILE_URI, params=params)

    def delete_file(self, filename):
        params = {
            'file': filename,
        }
        return self.__req(self.DELETE_FILE_URI, params=params)

    def convert_file(self, filename):
        params = {
            'file': filename,
        }
        return self.__req(self.CONVERT_FILE_URI, params=params)

    def file_converting_status(self, folder=None):
        params = []
        if folder is not None:
            params['folder'] = folder
        return self.__req(self.RUNNING_CONVERTS_URI, params=params)

    def get_splash_image(self, filename):
        params = {
            'file': filename,
        }
        return self.__req(self.GET_SPLASH_IMAGE_URI, params=params)

    def __req(self, uri, params=[]):
        payload = dict(params)
        if self.login is not None:
            payload['login'] = self.login
        if self.key is not None:
            payload['key'] = self.key
        resp = requests.get('{}{}'.format(self.API_HOST, uri), params=payload)
        if resp.status_code == 200:
            resp_data = resp.json()
            return ClientResponse(status=resp_data['status'], msg=resp_data['msg'], result=resp_data['result'])
        else:
            raise HttpException(status_code=resp.status_code)