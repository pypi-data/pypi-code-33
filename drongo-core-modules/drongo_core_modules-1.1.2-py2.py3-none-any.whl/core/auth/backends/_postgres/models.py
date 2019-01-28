from peewee import (BooleanField, CharField, DateTimeField, Model, Proxy,
                    TextField)

db = Proxy()


class User(Model):
    username = CharField(unique=True)
    password = CharField()
    active = BooleanField()
    superuser = BooleanField()
    created_on = DateTimeField()
    extras = TextField(null=True)

    class Meta:
        database = db
        table_name = 'auth_users'


class Group(Model):
    name = CharField(unique=True)
    extras = TextField(null=True)

    def add_user(self, username):
        if GroupUser.filter(group=self.name, user=username).count() == 0:
            GroupUser.create(group=self.name, user=username)

    def remove_user(self, username):
        if GroupUser.filter(group=self.name, user=username).count() > 0:
            GroupUser.delete().where(
                GroupUser.group == self.name and GroupUser.user == username
            ).execute()

    @classmethod
    def for_user(cls, username):
        return list(map(
            lambda item: item.group,
            GroupUser.filter(user=username)
        ))

    @property
    def users(self):
        return list(map(
            lambda item: item.user,
            GroupUser.filter(group=self.name)
        ))

    class Meta:
        database = db
        table_name = 'auth_groups'


class GroupUser(Model):
    group = CharField()
    user = CharField()

    class Meta:
        database = db
        table_name = 'auth_group_users'
        indexes = (
            (('group', 'user'), True),
        )


class ObjectOwner(Model):
    object_type = CharField()
    object_id = CharField()
    user = CharField()

    class Meta:
        database = db
        table_name = 'auth_object_owners'
        indexes = (
            (('object_type', 'object_id', 'user'), True),
        )


class Permission(Model):
    permission_id = CharField()
    client = CharField()

    class Meta:
        database = db
        table_name = 'auth_permissions'


class ObjectPermission(Model):
    object_type = CharField()
    object_id = CharField()
    permission_id = CharField()
    client = CharField()

    class Meta:
        database = db
        table_name = 'auth_object_permissions'
