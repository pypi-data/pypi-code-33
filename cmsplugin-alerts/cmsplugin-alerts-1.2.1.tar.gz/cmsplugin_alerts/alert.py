#
# Copyright 2017, Martin Owens <doctormo@gmail.com>
#
# This file is part of the software inkscape-web, consisting of custom 
# code for the Inkscape project's django-based website.
#
# inkscape-web is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# inkscape-web is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with inkscape-web.  If not, see <http://www.gnu.org/licenses/>.
#
"""
CMS page published alert/notification
"""

from django.utils.translation import ugettext_lazy as _, get_language
from django.conf import settings
from django.db.models import signals

from cms.models import Page
from cms.signals import post_publish

from alerts.base import BaseAlert
from alerts.fields import MultipleCheckboxField

#
# This cmsplugin_diff application is an optional extra, if it's
# not available, then you will still get notifications, but they'll
# be less useful as you won't be able to see any diff of what changed.
#
try:
    from cmsplugin_diff.models import PublishHistory
    this_sender = PublishHistory
    this_signal = signals.post_save
except ImportError:
    this_sender = Page
    this_signal = post_publish


class PagePublishedAlert(BaseAlert):
    name     = _("Website Page Published")
    desc     = _("A page on the website has been published after editing.")
    info     = _("When a website editor or translator edits one of the content pages, a message is sent to all subscribers. You can be subscribed to one page or all pages on the website.")
    sender   = this_sender

    subject       = "{% trans 'Published:' %} {{ instance }}"
    email_subject = "{% trans 'Published:' %} {{ instance }}"
    object_name   = "when the '{{ object }}' page is published"
    default_email = False
    signal        = this_signal

    subscribe_all = True
    subscribe_any = True
    subscribe_own = False

    def get_custom_fields(self, data, user=None):
        """Return the language filter field"""
        return [('lang',\
            MultipleCheckboxField(label=_('Language'), choices=settings.LANGUAGES, required=False,\
            help_text=_('Limit the notifications to this language only. Default is all languages.'))
                )]

    def call(self, *args, **kwargs):
        if 'language' not in kwargs:
            kwargs['language'] = get_language()
        if this_sender != Page:
            if not kwargs.get('created', False):
                return
            kwargs['history'] = kwargs['instance']
            kwargs['instance'] = kwargs['history'].page
        super(PagePublishedAlert, self).call(*args, **kwargs)

    def get_filter_subscriber(self, user, setting, kw, sub_type):
        """
        Filter by language, if the setting is not set, or the language setting is blank,
        this counts as 'all languages' and we send to all.
        """
        languages_needed = setting.get('lang', None)
        lang = '|%(language)s|' % kw
        print("Filtering subscription! {} {}".format(languages_needed, lang))
        return setting is None or languages_needed in ['', None] or lang in languages_needed
