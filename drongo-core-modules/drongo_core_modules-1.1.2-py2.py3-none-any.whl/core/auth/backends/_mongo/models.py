from mongobj.document import Document


class User(Document):
    __version__ = '1.0.0'
    __fields__ = [
        'username',
        'password',
        'active',
        'superuser',
        'created_on',
        'extras'
    ]


class Group(Document):
    __version__ = '1.0.0'
    __fields__ = [
        'name',
        'users',
        'extras'
    ]

    def add_user(self, username):
        if self.users is None:
            self.users = []

        if username not in self.users:
            self.users.append(username)

        self.save(force=True)

    def remove_user(self, username):
        if self.users is None:
            return

        if username in self.users:
            self.users.remove(username)
            self.save(force=True)

    @classmethod
    def for_user(cls, username):
        return list(map(
            lambda item: item.name,
            cls.objects.find(users=username)
        ))


class ObjectOwner(Document):
    __version__ = '1.0.0'
    __fields__ = [
        'object_type',
        'object_id',
        'user'
    ]


class Permission(Document):
    __version__ = '1.0.0'
    __fields__ = [
        'permission_id',
        'client'
    ]


class ObjectPermission(Document):
    __version__ = '1.0.0'
    __fields__ = [
        'object_type',
        'object_id',
        'permission_id',
        'client'
    ]
