import logging

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import UserManager as BaseUserManager
from django.core import validators
from django.db import models
from django.utils import timezone
from django.utils.crypto import salted_hmac
from django.utils.deconstruct import deconstructible
from django.utils.translation import ugettext_lazy as _

from ldapregister.models import LdapPerson
from limitmonitor import models as limitmonitor_models
from limitmonitor.task_resources import common as limitmonitor_common

log = logging.getLogger(__name__)


@deconstructible
class UsernameValidator(validators.RegexValidator):
    regex = r'^[A-Za-z][A-Za-z0-9]*$'
    message = _(
        'Enter a valid username. Must start with a letter, followed by letters and numbers.'
        ' No punctuation or special characters.'
    )


class UserManager(BaseUserManager):

    def create_user(self, username, email=None, password=None, **extra_fields):
        """Create regular users in LDAP, with no Django password."""

        return super(UserManager, self).create_user(username, email, password, **extra_fields)

    def create_superuser(self, username, email=None, password=None, **extra_fields):
        """Create superusers with a Django password."""

        return super(UserManager, self).create_superuser(username, email, password, **extra_fields)


class User(AbstractUser):
    objects = UserManager()
    REQUIRED_FIELDS = []
    username_validator = UsernameValidator()

    username = models.CharField(
        _('username'),
        max_length=150,
        unique=True,
        help_text=_('Required. Start with a letter, followed by letters and numbers.'),
        validators=[username_validator],
        error_messages={
            'unique': _("A user with that username already exists."),
        },
    )

    @classmethod
    def normalize_username(cls, username):
        username = super(User, cls).normalize_username(username)

        username = username.lower()
        suffix = "@" + settings.SITE_DOMAIN.lower()
        offset = 0 - len(suffix)

        if username.endswith(suffix):
            username = username[:offset]

        return username

    def get_ldap(self):
        return LdapPerson.objects.get(uid=self.get_username())

    def has_ldap(self):
        result = LdapPerson.objects.filter(uid=self.get_username())
        return len(result) == 1

    def create_ldap(self):
        username = self.get_username()
        mail = self.get_identity()
        LdapPerson.objects.create(uid=username, cn=username, sn=username, mail=mail)

    def set_ldap_password(self, raw_password):
        ldap_person = self.get_ldap()
        ldap_person.change_password(raw_password)

    def get_identity(self):
        return self.get_username() + "@" + settings.SITE_DOMAIN.lower()

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):

        # save django user
        super(User, self).save(force_insert, force_update, using, update_fields)

        # create LDAP user (if required)
        if not self.has_ldap():
            self.create_ldap()

        # force null Django password (will use LDAP password instead)
        self.set_unusable_password()

        # create any missing limits
        limitmonitor_models.create_missing_user_limits(self)

        # delete invalid credits (they will be re-parsed)
        limitmonitor_models.delete_unconverted_user_credits(self)

        if settings.DEBUG_ALL_ACCESS:

            ssh = limitmonitor_common.get_openvpn_ssh_connection()
            renewal_date = timezone.now() + timezone.timedelta(weeks=5200)

            for limit in limitmonitor_models.Limit.objects.filter(user=self, is_active=False):
                limitmonitor_common.activate_single_limit(ssh, limit, renewal_date=renewal_date)

            ssh.close()

    def set_password(self, raw_password):

        # force null Django password (will use LDAP password)
        self.set_unusable_password()

        # create LDAP user (if required)
        if self.get_username():

            if not self.has_ldap():
                self.create_ldap()

            # set LDAP password
            self.set_ldap_password(raw_password)

    def get_session_auth_hash(self):
        """
        Return an HMAC of the password field.
        """
        key_salt = "django.contrib.auth.models.AbstractBaseUser.get_session_auth_hash"
        return salted_hmac(key_salt, self.get_username()).hexdigest()  # FIXME: should use LDAP password value!
