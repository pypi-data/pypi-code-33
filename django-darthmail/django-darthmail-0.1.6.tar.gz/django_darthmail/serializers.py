from __future__ import absolute_import

from email.mime.base import MIMEBase

from django.core.serializers.json import DjangoJSONEncoder

from .message import EmailMultiAlternatives

try:
    encodabletype = unicode
except NameError:
    encodabletype = str


def _b64encode(content):
    from base64 import b64encode
    if isinstance(content, encodabletype):
        content = content.encode('utf8')
    return b64encode(content).decode('ascii')


class EmailSerializer(DjangoJSONEncoder):
    # some parameter names and the property names don't match in django.core.mail.message.EmailMessage;
    # we have to fix the mismatch when serializing.
    RENAME_FIELDS = {
        'extra_headers': 'headers',
    }

    def default(self, obj):
        res = dict()
        if isinstance(obj, EmailMultiAlternatives):
            res['alternatives'] = list(map(self._encodeTupleOrMime, obj.alternatives))
            res['attachments'] = list(map(self._encodeTupleOrMime, obj.attachments))
            keys = ['body', 'bcc', 'cc', 'extra_headers', 'from_email', 'reply_to', 'subject', 'to', 'metadata',
                    'send_at', 'do_not_send']
            for key in keys:
                dst_key = self.RENAME_FIELDS.get(key, key)
                try:
                    res[dst_key] = self._normalize(key, obj.__getattribute__(key))
                except AttributeError:
                    pass  # leave non-existing attributes empty
            return res
        elif isinstance(obj, MIMEBase):
            if obj.is_multipart():
                raise NotImplementedError('cannot serialize multipart MIME yet')

            headers = dict()
            for key in obj.keys():
                # these are managed by the MIME* type itself
                if key not in ['Content-Type', 'MIME-Version', 'Content-Transfer-Encoding']:
                    headers[key] = obj[key]

            # is this even a thing? I'm pretty sure we don't use anything else
            if obj['Content-Transfer-Encoding'] != 'base64':
                raise NotImplementedError(
                    'MIME object with unsupported transfer-encoding: %s' % obj['Content-Transfer-Encoding']
                )

            return dict(
                filename=obj.get_filename(),
                content=obj.get_payload(),  # already base64 encoded; see above
                mimetype=obj.get_content_type(),
                headers=headers,
            )
        return super(EmailSerializer, self).default(obj)

    def _normalize(self, key, val):
        if key == 'metadata':
            # The API expects metadata to be a dict with lists as values. To make the client simpler, we wrap scalars
            # in a list.
            for k, v in val.items():
                if not isinstance(v, list) and not isinstance(v, tuple):
                    val[k] = [v]
        return val

    def _encodeTupleOrMime(self, attachment):
        if isinstance(attachment, tuple):
            if len(attachment) == 2:
                return dict(
                    content=_b64encode(attachment[0]),
                    mimetype=attachment[1],
                )
            elif len(attachment) == 3:
                return dict(
                    filename=attachment[0],
                    content=_b64encode(attachment[1]),
                    mimetype=attachment[2],
                )
            else:
                raise TypeError('unsupported attachment/alternative format; tuple with %d elements' % len(attachment))
        elif isinstance(attachment, MIMEBase):
            return self.default(attachment)
        else:
            raise TypeError('unsupported attachment type %s' % type(attachment))
