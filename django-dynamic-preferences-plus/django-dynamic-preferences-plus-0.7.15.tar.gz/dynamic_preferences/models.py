# !/usr/bin/env python
# encoding:UTF-8

"""
Preference models, queryset and managers that handle the logic for persisting preferences.
"""
from django.db import models

from django.contrib.sites.models import Site
from django.db.models.signals import post_save
from django.conf import settings
from django.utils.functional import cached_property
from dynamic_preferences.registries import user_preferences_registry, site_preferences_registry, \
    global_preferences_registry
from django.core.files import File
from django.utils.translation import ugettext as _
from dynamic_preferences.types import FilePreference
from dynamic_preferences.utils import get_default_file_path


class PreferenceModelManager(models.Manager):
    def to_dict(self, **kwargs):
        """ 
            Return a dict of preference models values with the same structure as registries
            Used to access preferences value within templates
        """

        preferences = self.get_queryset().all()
        if kwargs:
            preferences = preferences.filter(**kwargs)

        d = {}
        for p in preferences:
            try:
                d[p.section][p.name] = p.value
            except KeyError:
                d[p.section] = {}
                d[p.section][p.name] = p.value

        return d


class BasePreferenceModel(models.Model):
    """
    A base model with common logic for all preferences models.
    """

    #: The section under which the preference is declared
    section = models.CharField(max_length=255, db_index=True, blank=True, null=True, default=None)

    #: a name for the preference
    name = models.CharField(max_length=255, db_index=True)

    #: a value, serialized to a string. This field should not be accessed directly,
    # use :py:attr:`BasePreferenceModel.value` instead
    raw_value = models.TextField(null=True, blank=True)

    #: Keep a reference to the whole preference registry.
    #: In order to map the Preference Model Instance to the Preference object.
    registry = None

    #: help text
    help = models.TextField(null=True, blank=True, default="")

    objects = PreferenceModelManager()

    class Meta:
        abstract = True
        app_label = 'dynamic_preferences'

    def __init__(self, *args, **kwargs):
        # Check if the model is already saved in DB

        v = kwargs.pop("value", None)
        super(BasePreferenceModel, self).__init__(*args, **kwargs)

        new = self.pk is None

        if new:
            if v is not None:
                if isinstance(self.registry[kwargs['section']][kwargs['name']], FilePreference):
                    # path = get_upload_file_path(v)
                    # if not os.path.exists(os.path.dirname(path)):
                    #     os.makedirs(os.path.dirname(path))
                    # shutil.copy2(get_default_file_path(v), path)
                    # self.value = open(path, 'wb+')
                    self.value = File(open(get_default_file_path(v), 'rb+'), name=v)
                else:
                    self.value = v
            else:
                self.value = self.preference.default

    @cached_property
    def preference(self):
        # return self.registry[self.section][self.name].initial
        # r = None
        # try:
        #     r = self.registry.get(section=self.section, name=self.name)
        # except:
        #     r = {}
        # return r
        return self.registry.get(section=self.section, name=self.name)

    def set_value(self, value):
        """
            Save serialized self.value to self.raw_value
        """
        self.raw_value = self.preference.serializer.serialize(value)

    def get_value(self):
        """
            Return deserialized self.raw_value
        """
        return self.preference.serializer.deserialize(self.raw_value)

    value = property(get_value, set_value)

    def __unicode__(self):
        return self.preference.identifier()


class GlobalPreferenceModel(BasePreferenceModel):
    registry = global_preferences_registry

    class Meta:
        unique_together = ('section', 'name')
        app_label = 'dynamic_preferences'
        verbose_name = _('global preference')
        verbose_name_plural = _('global preferences')


class UserPreferenceModel(BasePreferenceModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="preferences")
    registry = user_preferences_registry

    class Meta:
        unique_together = ('user', 'section', 'name')
        app_label = 'dynamic_preferences'
        verbose_name = _('user preference')
        verbose_name_plural = _('user preferences')


class SitePreferenceModel(BasePreferenceModel):
    site = models.ForeignKey(Site, related_name="preferences")
    registry = site_preferences_registry

    class Meta:
        unique_together = ('site', 'section', 'name')
        app_label = 'dynamic_preferences'
        verbose_name = _('site preference')
        verbose_name_plural = _('site preferences')


global_preferences = GlobalPreferenceModel.objects
site_preferences = SitePreferenceModel.objects
user_preferences = UserPreferenceModel.objects


# Create default preferences for new users
# Right now, only works if the model is django.contrib.auth.models.User
# And if settings.CREATE_DEFAULT_PREFERENCES_FOR_NEW_USERS is set to True in settings
def create_default_preferences(sender, **kwargs):
    create_default_preferencesfor_new_users = getattr(settings, 'CREATE_DEFAULT_PREFERENCES_FOR_NEW_USERS', True)
    if create_default_preferencesfor_new_users and settings.AUTH_USER_MODEL == "auth.User":
        # the object which is saved can be accessed via kwargs 'instance' key.
        obj = kwargs['instance']
        # created = kwargs.get("created")
        user_preferences_registry.create_default_preferences(obj)


if getattr(settings, 'CREATE_DEFAULT_PREFERENCES_FOR_NEW_USERS', True) and settings.AUTH_USER_MODEL == "auth.User":
    try:
        from django.contrib.auth import get_user_model
    except ImportError:  # django < 1.5
        from django.contrib.auth.models import User
    else:
        User = get_user_model()
    post_save.connect(create_default_preferences, sender=User)
