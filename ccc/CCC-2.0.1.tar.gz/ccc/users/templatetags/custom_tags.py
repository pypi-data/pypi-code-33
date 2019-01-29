from django import template

register = template.Library()


@register.simple_tag
def get_sent_usage(dict_usage):
    return dict_usage[0]


@register.simple_tag
def get_received_usage(dict_usage):
    return dict_usage[1]


@register.simple_tag
def get_sent_total(balance, key):
    voice = balance['voice_usage']
    mms  = balance['mms_usage']
    sms = balance['sms_usage']
    email = balance['email_usage']
    if key == "sent":
        total = voice[0] + mms[0] + sms[0] + email[0]
    else:
        total = voice[1] + mms[1] + sms[1] + email[1]
    return total
