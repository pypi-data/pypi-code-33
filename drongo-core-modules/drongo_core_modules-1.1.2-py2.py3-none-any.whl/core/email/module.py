import logging

from drongo_modules.core.module import Module


class Email(Module):
    """Drongo module for sending emails"""

    # Email Types
    MAILGUN = 'MAILGUN'

    __default_config__ = {
        'type': MAILGUN
    }

    logger = logging.getLogger('wing_database')

    def init(self, config):
        self.app.context.modules.email = self

        self._type = config.get('type')
        if self._type == self.MAILGUN:
            from .backends._mailgun import services

            self.services = services
        else:
            self.logger.error('Unknown mailer type!')
            raise NotImplementedError

        services.MailerServiceBase.init(module=self)

    def send_mail(self, from_email, to_email=[], cc=[], bcc=[], subject='',
                  text='', html=None, attachments=[]):
        print('Sending email...')
        self.services.SendEmailService(
            from_email=from_email, to_email=to_email, cc=cc, bcc=bcc,
            subject=subject, text=text, html=html, attachments=attachments
        ).call()
        print('Sent!')
