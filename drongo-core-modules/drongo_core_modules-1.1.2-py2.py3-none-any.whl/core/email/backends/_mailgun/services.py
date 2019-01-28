import requests


class MailerServiceBase(object):
    _key_dir = None

    @classmethod
    def init(cls, module):
        cls._api_domain = module.config.get('mailgun_domain')
        cls._api_key = module.config.get('mailgun_api_key')


class SendEmailService(MailerServiceBase):
    def __init__(self, from_email, to_email=[], cc=[], bcc=[], subject='',
                 text=None, html=None, attachments=[]):
        self.from_email = from_email
        self.to_email = to_email
        self.cc = cc
        self.bcc = bcc
        self.subject = subject
        self.text = text
        self.html = html
        self.attachments = attachments

    def call(self):
        url = 'https://api.mailgun.net/v3/{domain}/messages'.format(
            domain=self._api_domain)
        auth = ('api', self._api_key)
        data = {
            'from': self.from_email,
            'to': self.to_email,
            'subject': self.subject,
            'text': self.text
        }
        if self.html is not None:
            data['html'] = self.html
        if self.cc:
            data['cc'] = self.cc

        if self.bcc:
            data['bcc'] = self.bcc

        files = []
        for (name, fd) in self.attachments:
            files.append(
                ('attachment', (name, fd.read()))
            )

        requests.post(
            url,
            auth=auth,
            data=data,
            files=files
        )
