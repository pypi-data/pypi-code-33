from datetime import datetime, timedelta

import jwt
from passlib.hash import pbkdf2_sha256

from .models import (Group, GroupUser, ObjectOwner, ObjectPermission,
                     Permission, User, db)

HASHER = pbkdf2_sha256.using(rounds=10000)


class AuthServiceBase(object):
    @classmethod
    def init(cls, module):
        cls.module = module
        db.initialize(module.database.instance.get())
        module.database.instance.get().create_tables([
            User, Group, GroupUser, ObjectOwner, ObjectPermission, Permission
        ])


class UserForTokenService(AuthServiceBase):
    def __init__(self, token):
        self.token = token

    def call(self):
        token = self.token

        if token is None:
            return None

        try:
            token = jwt.decode(
                token, self.module.config.token_secret, algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            return None
        except Exception:
            return None

        username = token.get('username')
        return User.get(username=username)


class UserCreateService(AuthServiceBase):
    def __init__(self, username, password, active=False, superuser=False):
        self.username = username
        self.password = HASHER.hash(password)
        self.active = active
        self.superuser = superuser

    def check_exists(self):
        return User.filter(username=self.username).count() > 0

    def call(self, ctx=None):
        if self.check_exists():
            raise Exception('User already exists.')

        return User.create(
            username=self.username,
            password=self.password,
            active=self.active,
            superuser=self.superuser,
            created_on=datetime.utcnow()
        )


class UserChangePasswordService(AuthServiceBase):
    def __init__(self, username, password):
        self.username = username
        self.password = HASHER.hash(password)

    def call(self):
        user = User.get(username=self.username, active=True)
        user.password = self.password
        user.save()


class UserLoginService(AuthServiceBase):
    def __init__(self, username, password):
        self.username = username
        self.password = password

    def check_credentials(self):
        if User.filter(username=self.username, active=True).count() == 0:
            return False

        user = User.get(username=self.username, active=True)
        return HASHER.verify(self.password, user.password)

    def create_token(self):
        user = User.get(username=self.username, active=True)
        token = jwt.encode({
            'username': user.username,
            'iat': datetime.utcnow(),
            'exp': datetime.utcnow()
            + timedelta(seconds=self.module.config.token_age)
        }, self.module.config.token_secret, algorithm='HS256')
        return token.decode('ascii')


class UserLogoutService(AuthServiceBase):
    def expire_token(self, token):
        pass

    def call(self, ctx):
        pass


class UserTokenRefresh(AuthServiceBase):
    def __init__(self, token):
        self.token = token

    def call(self):
        try:
            token = jwt.decode(
                self.token, self.module.config.token_secret,
                algorithms=['HS256'])
            token.update({
                'iat': datetime.utcnow(),
                'exp': datetime.utcnow()
                + timedelta(seconds=self.module.config.token_age)
            })
            return jwt.encode(
                token, self.module.config.token_secret, algorithm='HS256'
            ).decode('ascii')
        except jwt.ExpiredSignatureError:
            return None
        except Exception:
            return None


class UserListService(AuthServiceBase):
    def call(self, ctx):
        return User.select()


class UserActivateService(AuthServiceBase):
    def __init__(self, username):
        self.username = username

    def call(self):
        user = User.get(username=self.username)
        if user is not None:
            user.active = True
            user.save()


class UserDeactivateService(AuthServiceBase):
    def __init__(self, username):
        self.username = username

    def call(self):
        user = User.get(username=self.username)
        if user is not None:
            user.active = False
            user.save()


class GroupCreateService(AuthServiceBase):
    def __init__(self, name):
        self.name = name

    def call(self):
        if Group.filter(name=self.name).count() > 0:
            return Group.get(name=self.name)

        else:
            return Group.create(name=self.name)


class GroupDeleteService(AuthServiceBase):
    def __init__(self, name):
        self.name = name

    def call(self):
        if Group.filter(name=self.name).count() > 0:
            Group.get(name=self.name).delete_instance()


class GroupListService(AuthServiceBase):
    def call(self):
        return Group.select()


class GroupUserAddService(AuthServiceBase):
    def __init__(self, name, username):
        self.name = name
        self.username = username

    def call(self):
        group = Group.get_or_none(name=self.name)
        if group is None:
            group = Group.create(name=self.name)

        group.add_user(self.username)


class GroupUserDeleteService(AuthServiceBase):
    def __init__(self, name, username):
        self.name = name
        self.username = username

    def call(self):
        group = Group.get(name=self.name)
        if group is None:
            return

        group.remove_user(self.username)


class GroupUserListService(AuthServiceBase):
    def __init__(self, name):
        self.name = name

    def call(self):
        group = Group.get(name=self.name)
        if group is None:
            return []

        return group.users


class GroupsForUserListService(AuthServiceBase):
    def __init__(self, username):
        self.username = username

    def call(self):
        return Group.for_user(username=self.username)


class ObjectOwnerGetService(AuthServiceBase):
    def __init__(self, object_type, object_id):
        self.object_type = object_type
        self.object_id = object_id

    def call(self):
        owner = ObjectOwner.get_or_none(
            object_type=self.object_type, object_id=self.object_id)

        if owner is not None:
            return owner.user


class ObjectOwnerSetService(AuthServiceBase):
    def __init__(self, object_type, object_id, username):
        self.object_type = object_type
        self.object_id = object_id
        self.username = username

    def call(self):
        owner = ObjectOwner.get_or_none(
            object_type=self.object_type, object_id=self.object_id)

        if owner is not None:
            owner.user = self.username
            owner.save()
        else:
            ObjectOwner.create(
                object_type=self.object_type,
                object_id=self.object_id,
                user=self.username
            )


class PermissionCheckService(AuthServiceBase):
    def __init__(self, permission_id, username):
        self.permission_id = permission_id
        self.username = username

    def call(self):
        user = User.get_or_none(username=self.username, active=True)
        if user is None:
            return False

        if user.superuser:
            return True

        permission = Permission.get_or_none(
            permission_id=self.permission_id, client='user.' + self.username)
        if permission is not None:
            return True

        groups = list(map(
            lambda group: 'group.{group}'.format(group=group),
            Group.for_user(self.username)
        ))
        if len(groups) > 0:
            g1 = groups[0]
            q = (Permission.client == g1)
            for g in groups[1:]:
                q = q or (Permission.client == g)
        permission = Permission.select().where(
            Permission.permission_id == self.permission_id and (
                q
            )
        ).count()
        if permission > 0:
            return True

        return False


class PermissionSetService(AuthServiceBase):
    def __init__(self, permission_id, client):
        self.permission_id = permission_id
        self.client = client

    def call(self):
        permission = Permission.get_or_none(
            permission_id=self.permission_id,
            client=self.client
        )
        if permission is None:
            Permission.create(
                permission_id=self.permission_id,
                client=self.client
            )


class PermissionUnsetService(AuthServiceBase):
    def __init__(self, permission_id, client):
        self.permission_id = permission_id
        self.client = client

    def call(self):
        permission = Permission.get_or_none(
            permission_id=self.permission_id,
            client=self.client
        )
        if permission is not None:
            permission.delete_instance()


class ObjectPermissionCheckService(AuthServiceBase):
    def __init__(self, object_type, object_id, permission_id, username):
        self.object_type = object_type
        self.object_id = object_id
        self.permission_id = permission_id
        self.username = username

    def call(self):
        user = User.get_or_none(username=self.username, active=True)
        if user is None:
            return False

        if user.superuser:
            return True

        permission = ObjectPermission.get_or_none(
            object_type=self.object_type, object_id=self.object_id,
            permission_id=self.permission_id, client='user.' + self.username)
        if permission is not None:
            return True

        groups = list(map(
            lambda group: 'group.{group}'.format(group=group),
            Group.for_user(self.username)
        ))
        if len(groups) > 0:
            g1 = groups[0]
            q = (ObjectPermission.client == g1)
            for g in groups[1:]:
                q = q or (ObjectPermission.client == g)
        permission = ObjectPermission.select().where(
            ObjectPermission.object_type == self.object_type and
            ObjectPermission.object_id == self.object_id and
            ObjectPermission.permission_id == self.permission_id and q
        ).count()
        if permission > 0:
            return True

        return False


class ObjectPermissionSetService(AuthServiceBase):
    def __init__(self, object_type, object_id, permission_id, client):
        self.object_type = object_type
        self.object_id = object_id
        self.permission_id = permission_id
        self.client = client

    def call(self):
        permission = ObjectPermission.get_or_none(
            object_type=self.object_type,
            object_id=self.object_id,
            permission_id=self.permission_id,
            client=self.client
        )
        if permission is None:
            ObjectPermission.create(
                object_type=self.object_type,
                object_id=self.object_id,
                permission_id=self.permission_id,
                client=self.client
            )


class ObjectPermissionUnsetService(AuthServiceBase):
    def __init__(self, object_type, object_id, permission_id, client):
        self.object_type = object_type
        self.object_id = object_id
        self.permission_id = permission_id
        self.client = client

    def call(self):
        permission = ObjectPermission.get_or_none(
            object_type=self.object_type,
            object_id=self.object_id,
            permission_id=self.permission_id,
            client=self.client
        )
        if permission is not None:
            permission.delete_instance()


class PermissionListForClientService(AuthServiceBase):
    def __init__(self, client):
        self.client = client

    def call(self):
        return list(map(
            lambda item: item.permission_id,
            Permission.select().where(Permission.client == self.client)
        ))
