from django.db import models
from django.contrib.auth import models as auth_models
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone


class ConsumerManager(auth_models.BaseUserManager):

    def create_user(self, kong_consumer_id, password=None, **extra_fields):
        """
        Creates and saves a User with the given username, email and
        password.
        """
        now = timezone.now()

        if not kong_consumer_id:
            raise ValueError('Users must have a kong_consumer_id')

        consumer = self.model(
            kong_consumer_id=kong_consumer_id,

            is_active=True,
            is_superuser=False,
            last_login=now, created_at=now, **extra_fields)

        if password:
            consumer.set_password(password)

        consumer.save(using=self._db)
        return consumer

    def create_superuser(self, kong_consumer_id, password, **extra_fields):
        u = self.create_user(kong_consumer_id, password, **extra_fields)
        u.is_staff = True
        u.is_active = True
        u.is_superuser = True
        u.save(using=self._db)
        return u


class Consumer(auth_models.AbstractBaseUser, auth_models.PermissionsMixin):
    is_staff = models.BooleanField(
        _('Staff status'), default=False,
        help_text=_('Designates whether the user can log into this admin '
                    'site.'))
    is_active = models.BooleanField(
        _('Active'), default=True,
        help_text=_('Designates whether this user should be treated as '
                    'active. Unselect this instead of deleting accounts.'))

    kong_consumer_id = models.CharField(max_length=36, unique=True)

    created_at = models.DateTimeField(_('date joined'), default=timezone.now)
    updated_at = models.DateTimeField(_('date updated'), null=True, blank=True)

    objects = ConsumerManager()

    USERNAME_FIELD = 'kong_consumer_id'
    REQUIRED_FIELDS = []

    @property
    def classname(self):
        return self.__class__.__name__.lower()

    @property
    def is_alive(self):
        return self.is_active

    class Meta:
        verbose_name = _('Consumer')
        verbose_name_plural = _('Consumers')

    def get_full_name(self):
        return self.kong_consumer_id

    def get_short_name(self):
        return self.get_full_name()

    def __str__(self):
        return self.get_full_name()
