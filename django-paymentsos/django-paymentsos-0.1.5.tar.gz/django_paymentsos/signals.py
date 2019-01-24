import django.dispatch

valid_notification_received = django.dispatch.Signal(providing_args=['instance'])
invalid_notification_received = django.dispatch.Signal(providing_args=['instance'])

notification_flagged = django.dispatch.Signal(providing_args=['instance'])

notification_type_payment_create = django.dispatch.Signal(providing_args=['instance'])
notification_type_charge_create = django.dispatch.Signal(providing_args=['instance'])

transaction_result_succeed = django.dispatch.Signal(providing_args=['instance'])
transaction_result_failed = django.dispatch.Signal(providing_args=['instance'])
transaction_result_pending = django.dispatch.Signal(providing_args=['instance'])
