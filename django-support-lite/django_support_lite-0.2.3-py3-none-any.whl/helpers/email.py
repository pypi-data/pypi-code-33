from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string


def send(request, to, title, template, context):
    if not hasattr(settings, 'DSL_EMAIL_ENABLE') or not settings.DSL_EMAIL_ENABLE:
        return

    email = EmailMultiAlternatives(
        title,
        render_to_string(
            'emails/{}.txt'.format(template),
            context,
            request
        ),
        settings.DSL_EMAIL_SENDER,
        [to]
    )
    email.attach_alternative(
        render_to_string(
            'emails/{}.html'.format(template),
            context,
            request
        ),
        "text/html"
    )
    email.send()
