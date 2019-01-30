# !/usr/bin/env python
# encoding:UTF-8

from django.core.management.base import BaseCommand
from dynamic_preferences.models import GlobalPreferenceModel, UserPreferenceModel, SitePreferenceModel
from django.contrib.sites.models import Site
from dynamic_preferences.registries import autodiscover, global_preferences_registry, user_preferences_registry, \
    site_preferences_registry


def delete_preferences(queryset):
    """
    Delete preferences objects if they are not present in registry. Return a list of deleted objects
    """
    deleted = []
    # Iterate through preferences. If an error is raised when accessing preference object, just delete it
    for p in queryset:
        try:
            p.preference
        except KeyError:
            p.delete()
            deleted.append(p)
    return deleted


class Command(BaseCommand):
    help = "Find and delete preferences from database if they don't exist in registries. Create preferences that are " \
           "not present in database"

    def handle(self, *args, **options):
        autodiscover()
        deleted = delete_preferences(GlobalPreferenceModel.objects.all())
        print "Deleted %s global preference models : %s" % \
            (len(deleted), ", ".join(['Section: %s - Name: %s' % (p.section, p.name) for p in deleted]))

        deleted = delete_preferences(UserPreferenceModel.objects.all())
        print "Deleted %s user preference models : %s" % \
            (len(deleted), ", ".join(['Section: %s - Name: %s' % (p.section, p.name) for p in deleted]))

        deleted = delete_preferences(SitePreferenceModel.objects.all())
        print "Deleted %s site preference models : %s" % \
            (len(deleted), ", ".join(['Section: %s - Name: %s' % (p.section, p.name) for p in deleted]))

        # Create needed preferences
        # Global
        preferences = global_preferences_registry.preferences()
        for p in preferences:
            p.to_model(**{"help": p.help})
        print 'Created/updated %s default global preferences' % len(preferences)

        # User
        preferences = user_preferences_registry.preferences()
        try:
            from django.contrib.auth import get_user_model
        except ImportError:  # django < 1.5
            from django.contrib.auth.models import User
        else:
            User = get_user_model()
        users = list(User.objects.all())
        for user in users:
            for p in preferences:
                p.to_model(user=user, **{"help": p.help})
        print 'Created/updated default preferences for %s users' % len(users)

        # Site
        preferences = site_preferences_registry.preferences()
        try:
            site = Site.objects.get(pk=1)
        except Site.DoesNotExist:
            print 'Cannot create default preference for first site. Please create add at least one site in your ' \
                  'database.'
            site = None
        if site is not None:
            for p in preferences:
                p.to_model(site=site, **{"help": p.help})
            print 'Created/updated %s default preferences for first site' % len(preferences)
