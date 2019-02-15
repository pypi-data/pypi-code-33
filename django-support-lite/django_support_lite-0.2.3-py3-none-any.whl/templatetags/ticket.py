from django.template import Library

from django_support_lite.enums import Priority, ResponseType, Status

register = Library()

@register.filter
def ticket_state_label(ticket):
    if ticket.status == Status.OPEN:
        return ResponseType.label(ticket.response_type)

    return Status.label(ticket.status)

@register.filter
def ticket_state_css_class(ticket):
    if ticket.status in (Status.CLOSE, Status.ARCHIVE):
        return 'light'

    if ticket.response_type == ResponseType.USER_RESPONSE:
        return 'primary'

    if ticket.response_type == ResponseType.SUPPORT_RESPONSE:
        return 'secondary'

    raise ValueError('Response type not supported yet.')

@register.filter
def ticket_priority_label(priority):
    return Priority.label(priority)

@register.filter
def ticket_priority_css_class(priority):
    if priority == Priority.NORMAL:
        return 'success'

    if priority == Priority.MODERATE:
        return 'warning'

    if priority == Priority.HIGH:
        return 'danger'

    raise ValueError('Priority not supported yet.')
