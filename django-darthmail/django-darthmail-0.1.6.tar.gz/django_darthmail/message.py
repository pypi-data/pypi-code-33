import os
import mimetypes
from email.mime.image import MIMEImage

from django.core.mail import EmailMultiAlternatives as DjangoEmailMultiAlternatives


class EmailMultiAlternatives(DjangoEmailMultiAlternatives):
    def __init__(self, *args, **kwargs):
        """
        Extension of django's EmailMultiAlternatives supporting two extra parameters: metadata and send_at.

        @param metadata: a dict where each value is either a scalar (int, str, etc) or a list of scalars.
        @param send_at: date when to actually send the email.
        """
        self.metadata = kwargs.pop('metadata', dict())
        self.send_at = kwargs.pop('send_at', None)

        super(EmailMultiAlternatives, self).__init__(*args, **kwargs)

    def attach_inline_image(self, filepath, cid):
        if not os.path.exists(filepath):
            # TODO: shouldn't we raise something?
            return
        with open(filepath, 'rb') as fp:
            msg_img = MIMEImage(fp.read())
            msg_img.add_header('Content-ID', '<{}>'.format(cid))
            self.attach(msg_img)

    def add_image(self, directory, filename, alias):
        '''
        Wrapper for backward-compat with notification.models.EmailMultiAlternativesWithImages
        '''
        self.attach_inline_image(os.path.join(directory, filename), alias)

    def add_attachment(self, _file):
        content_type, encoding = mimetypes.guess_type(_file.name)
        self.attach(os.path.basename(_file.name), _file.read(), content_type)
