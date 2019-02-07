from paymentcorner.http import Http


class Auth(Http):

    def authenticate(self):
        return self.post(self.config.ENDPOINT_URLS['login'], {
            'email': self.config.email,
            'password': self.config.password,
            'session_time': 5
        }, authenticated=False, retry=False)
