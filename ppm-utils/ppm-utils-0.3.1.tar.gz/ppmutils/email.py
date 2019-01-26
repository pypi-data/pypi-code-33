from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.conf import settings

import logging
logger = logging.getLogger(__name__)


def send(subject=None, recipients=None, template=None, context=None):
    """
    Send an e-mail to a list of participants with the given subject and message. 
    Extra is dictionary of variables to be swapped into the template.
    """

    # Build the message content
    msg_html = render_to_string('email/%s.html' % template, context)
    msg_plain = render_to_string('email/%s.txt' % template, context)

    try:
        # Send it
        msg = EmailMultiAlternatives(subject, msg_plain, settings.DEFAULT_FROM_EMAIL, recipients)
        msg.attach_alternative(msg_html, "text/html")
        msg.send()

        logger.debug('Emails {} -> {} sent!'.format(subject, recipients))

        return True

    except Exception as e:
        logger.exception('Emails could not be sent: {}'.format(e), exc_info=True,
                         extra={'recipients': recipients, 'subject': subject, 'template': template})

    return False
