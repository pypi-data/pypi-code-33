from datetime import timedelta
from django.template.defaultfilters import timeuntil
from django.utils.timezone import now


def get_next_time(obj):
    """Get humanized form of next run."""
    next_ = obj.next_time
    if next_ is None:
        return
    dst_date = now() + timedelta(seconds=next_)
    return timeuntil(dst_date)
