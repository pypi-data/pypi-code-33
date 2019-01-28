import re


class UsernameValidator(object):
    def __init__(self, api, username):
        self.api = api
        self.username = username

    def validate(self):
        if self.username is None or self.username == '':
            self.api.error(
                'username',
                'Username cannot be empty.'
            )
            return False

        m = re.match('[a-zA-Z][a-zA-Z0-9.]*', self.username)
        if (not m) or (m.group() != self.username):
            self.api.error(
                'username',
                'Only alpha number characters and underscore is allowed.'
            )
            return False

        return True


class PasswordValidator(object):
    def __init__(self, api, password):
        self.api = api
        self.password = password

    def validate(self):
        if self.password is None or self.password == '':
            self.api.error(
                'password',
                'Password cannot be empty.'
            )
            return False

        if len(self.password) < 5:
            self.api.error(
                'password',
                'Password must be at least 5 characters.'
            )
            return False
        return True
