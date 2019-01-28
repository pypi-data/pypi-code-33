from drongo import Drongo


class AuthApp(Drongo):
    def init(self):
        from drongo_modules.core.auth import Auth
        from drongo_modules.core.auth.middleware import AuthMiddleware

        from drongo_modules.core.database import Database

        Database(
            self,
            _id='main',
            name='drongo_master',
            type=Database.MONGO
        )

        Auth(
            self,
            database='main',
            enable_api=True,
            create_admin_user=True,
            admin_password='admin123',
            active_on_register=True,
            token_secret='somerandomsecretfortest',
            token_age=5
        )
        self.add_middleware(AuthMiddleware())


class AuthClient(object):
    def __init__(self, api_client):
        self.client = api_client

    def me(self):
        resp = self.client.get('/auth/users/me')
        if resp['status'] == 'ERROR':
            return None
        else:
            return resp['payload']

    def login(self, username, password):
        login_data = dict(username=username, password=password)
        resp = self.client.post('/auth/users/operations/login', login_data)
        if resp['status'] == 'OK':
            self.client.set_auth_token(resp['payload']['token'])
        else:
            raise Exception('Login error!')

    def refresh(self):
        resp = self.client.get(
            '/auth/users/operations/refresh-token')
        new_token = resp['payload']['token']
        self.client.set_auth_token(new_token)

    def logout(self):
        self.client.get('/auth/users/operations/logout')
        self.client.set_auth_token(None)

    def register(self, username, password):
        login_data = dict(username=username, password=password)
        resp = self.client.post('/auth/users/', login_data)
        if resp['status'] == 'OK':
            return True
        else:
            return False

    def change_password(self, password=None, new_password=None, username=None):
        change_pwd_data = dict(new_password=new_password)
        if username is not None:
            change_pwd_data['username'] = username
        if password is not None:
            change_pwd_data['password'] = password

        self.client.post(
            '/auth/users/operations/change-password', change_pwd_data)

    def get_user_list(self):
        resp = self.client.get('/auth/users')
        if resp['status'] == 'OK':
            return resp['payload']
        else:
            return None

    def get_group_list(self):
        resp = self.client.get('/auth/groups')
        if resp['status'] == 'OK':
            return resp['payload']
        else:
            return None

    def create_group(self, name):
        group_data = dict(name=name)
        resp = self.client.post('/auth/groups', group_data)
        return resp['status'] == 'OK'

    def delete_group(self, name):
        resp = self.client.delete('/auth/groups/' + name)
        return resp['status'] == 'OK'

    def add_user_to_group(self, group, username):
        user_data = dict(username=username)
        resp = self.client.post(
            '/auth/groups/{group}/users'.format(group=group), user_data)
        return resp['status'] == 'OK'

    def delete_user_from_group(self, group, username):
        resp = self.client.delete(
            '/auth/groups/{group}/users/{username}'.format(
                group=group, username=username))
        return resp['status'] == 'OK'

    def get_group_users(self, group):
        resp = self.client.get(
            '/auth/groups/{group}/users'.format(group=group))
        if resp['status'] == 'OK':
            return resp['payload']

    def get_user_groups(self, username):
        resp = self.client.get(
            '/auth/users/{username}/groups'.format(username=username))
        if resp['status'] == 'OK':
            return resp['payload']
        else:
            return None

    def set_owner(self, object_type, object_id, username):
        owner_data = dict(username=username)
        self.client.post(
            '/auth/objects/{object_type}/{object_id}/'
            'operations/set-owner'.format(
                object_type=object_type,
                object_id=object_id),
            owner_data
        )

    def get_owner(self, object_type, object_id):
        resp = self.client.get(
            '/auth/objects/{object_type}/{object_id}/owner'.format(
                object_type=object_type,
                object_id=object_id)
        )
        if resp['status'] == 'OK':
            return resp['payload']

    def permission_set(self, permission_id, client):
        data = dict(client=client)
        self.client.post(
            '/auth/permissions/{permission_id}/'.format(
                permission_id=permission_id),
            data
        )

    def object_permission_set(self, object_type, object_id, permission_id,
                              client):
        data = dict(client=client)
        self.client.post(
            '/auth/permissions/{permission_id}/objects/'
            '{object_type}/{object_id}'.format(
                object_type=object_type,
                object_id=object_id,
                permission_id=permission_id
            ),
            data
        )

    def permission_check(self, permission_id, username):
        data = dict(username=username)
        resp = self.client.post(
            '/auth/permissions/{permission_id}/check'.format(
                permission_id=permission_id),
            data
        )
        if resp['status'] == 'OK':
            return resp['payload']

    def object_permission_check(self, object_type, object_id, permission_id,
                                username):
        data = dict(username=username)
        resp = self.client.post(
            '/auth/permissions/{permission_id}/objects/'
            '{object_type}/{object_id}/check'.format(
                permission_id=permission_id,
                object_type=object_type,
                object_id=object_id
            ),
            data
        )
        if resp['status'] == 'OK':
            return resp['payload']

    def permission_list(self, client):
        resp = self.client.get(
            '/auth/permissions/for/{client}'.format(
                client=client))
        if resp['status'] == 'OK':
            return resp['payload']
