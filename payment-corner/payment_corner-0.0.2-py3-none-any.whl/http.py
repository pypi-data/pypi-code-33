from paymentcorner.error import *


class Http(object):
    def __init__(self, config):
        self.config = config
        self.session = self.config.session

    def get(self, endpoint, query=None, authenticated=True):
        url = self.__url(endpoint)
        headers = self.__headers(authenticated)

        response = self.session.get(url, headers=headers, params=query)

        return self.__errors(response)

    def post(self, endpoint, data, authenticated=True, retry=True):

        url = self.__url(endpoint)
        headers = self.__headers(authenticated)
        response = self.__auth_error(retry,
                                     url,
                                     headers,
                                     data,
                                     authenticated)
        return self.__errors(response)

    def __url(self, endpoint):
        return self.config.environment_url() + endpoint

    HTTP_CODE_TO_ERROR = {
        400: BadRequestError,
        401: AuthenticationError,
        403: ForbiddenError,
        404: NotFoundError,
        429: TooManyRequestsError,
        405: MethodNotAllowed,
        408: RequestTimeout,
        412: PreconditionFailed,
        500: InternalError,
        503: ServiceUnavailable
    }

    def __errors(self, response):
        if int(response.status_code / 100) == 2:
            return response.json()
        elif 'error' in response.json():
            klass = Http.HTTP_CODE_TO_ERROR.get(response.status_code, Error)
            raise klass(response.status_code, response.json()['error'])

    def __auth_error(self, retry, url, headers, data, authenticated):
        retry_count = 3 if retry else 1
        response = None
        while retry_count:
            retry_count -= 1
            response = self.session.post(url, headers=headers, data=data)

            if response.status_code != 401:
                return response

            if retry:
                self.config.a()
                headers = self.__headers(authenticated)

        return response

    def __headers(self, authenticated):
        headers = {}

        if authenticated:
            headers = {'auth_token': self.config.token}

        return headers
