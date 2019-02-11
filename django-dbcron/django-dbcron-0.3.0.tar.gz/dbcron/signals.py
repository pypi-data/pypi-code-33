import django.dispatch

job_started = django.dispatch.Signal(providing_args=['job'])
job_done = django.dispatch.Signal(providing_args=['job'])
job_failed = django.dispatch.Signal(providing_args=['job'])
