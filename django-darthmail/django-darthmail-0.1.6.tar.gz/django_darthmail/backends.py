from __future__ import absolute_import
import logging

from django.conf import settings
from django.core.mail.backends.base import BaseEmailBackend
from django.utils.module_loading import import_string

from . import DarthMailError
from .message import EmailMultiAlternatives
from .client import DarthMailClient

logger = logging.getLogger(__name__)


class DarthMailBackend(BaseEmailBackend):
    def __init__(self, url=None, token=None, fallback=None, *args, **kwargs):
        self.client = DarthMailClient(
            url or settings.EMAIL_DARTHMAIL_URL,
            token or settings.EMAIL_DARTHMAIL_TOKEN,
        )
        try:
            self.fallback = import_string(fallback or settings.EMAIL_DARTHMAIL_FALLBACK)(*args, **kwargs)
        except ImportError:
            self.fallback = None
        super(DarthMailBackend, self).__init__(*args, **kwargs)

    def send_messages(self, email_messages):
        for msg in email_messages:
            # EmailMessage might try to cache the connection; not useful in our case.
            # Also breaks fallback logic.
            msg.connection = None

            if isinstance(msg, EmailMultiAlternatives):
                logger.info('submitting %s to darthmail', msg)
                try:
                    self.client.submit(msg)
                except Exception:
                    if not self.fail_silently:
                        raise
            elif self.fallback:
                logger.info('submitting %s through fallback backend (%s)', msg, self.fallback)
                self.fallback.send_messages(email_messages)
            else:
                raise DarthMailError('no fallback configured for non-darthmail messages. Set EMAIL_DARTHMAIL_FALLBACK.')
