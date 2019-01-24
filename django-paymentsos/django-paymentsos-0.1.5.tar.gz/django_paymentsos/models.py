from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from django_paymentsos import signals
from django_paymentsos.enumerators import ResultStatus, EventType
from django_paymentsos.fields import JSONField
from django_paymentsos.utils import get_signature


class ProviderSpecificData(models.Model):
    device_fingerprint = JSONField(blank=True)
    additional_details = JSONField(blank=True)

    class Meta:
        abstract = True


class PaymentMethod(models.Model):
    type = models.CharField(max_length=100, blank=True)
    token = models.CharField(max_length=100, blank=True)
    token_type = models.CharField(max_length=100, blank=True)
    holder_name = models.CharField(max_length=100, blank=True)
    expiration_date = models.CharField(max_length=100, blank=True)
    last_4_digits = models.CharField(max_length=100, blank=True)
    pass_luhn_validation = models.BooleanField(default=False)
    fingerprint = models.CharField(max_length=100, blank=True)
    bin_number = models.CharField(max_length=100, blank=True)
    vendor = models.CharField(max_length=100, blank=True)
    issuer = models.CharField(max_length=100, blank=True)
    card_type = models.CharField(max_length=100, blank=True)
    level = models.CharField(max_length=100, blank=True)
    country_code = models.CharField(max_length=100, blank=True)
    method_created = models.CharField(max_length=100, blank=True)
    billing_address = JSONField(blank=True)

    class Meta:
        abstract = True


class Result(models.Model):
    result_status = models.CharField(max_length=100, blank=True)
    category = models.CharField(max_length=100, blank=True)
    sub_category = models.CharField(max_length=100, blank=True)
    result_description = models.CharField(max_length=100, blank=True)

    class Meta:
        abstract = True

    def get_status(self):
        try:
            return ResultStatus(self.result_status)
        except ValueError:
            return self.result_status

    @property
    def is_result_status_succeed(self):
        return self.get_status() == ResultStatus.SUCCEED

    @property
    def is_result_status_failed(self):
        return self.get_status() == ResultStatus.FAILED

    @property
    def is_result_status_pending(self):
        return self.get_status() == ResultStatus.PENDING


class ProviderData(models.Model):
    provider_name = models.CharField(max_length=100, blank=True)
    response_code = models.CharField(max_length=100, blank=True)
    provider_description = models.CharField(max_length=100, blank=True)
    raw_response = JSONField(blank=True)
    transaction_id = models.CharField(max_length=100, blank=True)
    external_id = models.CharField(max_length=100, blank=True)

    class Meta:
        abstract = True


class Flag(models.Model):
    DUPLICATED_WEBHOOK = '1001'
    INVALID_SIGN = '1002'
    FLAG_CODES = (
        (DUPLICATED_WEBHOOK, 'Duplicated Webhook'),
        (INVALID_SIGN, 'Invalid Sign'),
    )
    flag = models.BooleanField(default=False)
    flag_code = models.CharField(max_length=4, blank=True, choices=FLAG_CODES)
    flag_info = models.CharField(max_length=100, blank=True)

    class Meta:
        abstract = True

    @property
    def is_flagged(self):
        return self.flag

    def save(self, *args, **kwargs):
        exists = PaymentsOSNotification.objects.filter(webhook_id=self.webhook_id).exists()
        if not self.id and exists:
            self.flag = True
            self.flag_code = self.DUPLICATED_WEBHOOK
            self.flag_info = 'Duplicate webhook_id.'
        super().save(*args, **kwargs)


class PaymentNotification(ProviderSpecificData, PaymentMethod, Result, ProviderData, Flag):
    data_id = models.CharField(max_length=100, blank=True)
    reconciliation_id = models.CharField(max_length=100, blank=True)
    amount = models.CharField(max_length=100, blank=True)
    notification_created = models.CharField(max_length=100, blank=True)

    currency = models.CharField(max_length=100, blank=True)  # payment.payment.create
    modified = models.CharField(max_length=100, blank=True)  # payment.payment.create
    statement_soft_descriptor = models.CharField(max_length=100, blank=True)  # payment.payment.create
    status = models.CharField(max_length=100, blank=True)  # payment.payment.create

    class Meta:
        abstract = True


class PaymentsOSNotification(PaymentNotification):
    webhook_id = models.CharField(max_length=100, blank=True)

    payment_id = models.CharField(max_length=100, blank=True)
    account_id = models.CharField(max_length=100, blank=True)
    app_id = models.CharField(max_length=100, blank=True)

    x_zooz_request_id = models.CharField(max_length=100, blank=True)
    x_payments_os_env = models.CharField(max_length=100, blank=True)
    version = models.CharField(max_length=100, blank=True)
    event_type = models.CharField(max_length=100, blank=True)
    signature = models.CharField(max_length=100, blank=True)

    created = models.DateTimeField()

    raw = JSONField()

    date_modified = models.DateTimeField(auto_now=True)
    date_created = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'paymentsos_notification'
        verbose_name = 'PaymentsOS Notification'
        verbose_name_plural = 'PaymentsOS Notifications'

    @property
    def is_event_type_payment_create(self):
        return self.get_event_type() == EventType.PAYMENT_CREATE

    @property
    def is_event_type_charge_create(self):
        return self.get_event_type() == EventType.CHARGE_CREATE

    @property
    def is_test(self):
        return True if self.x_payments_os_env == 'test' else False

    def get_event_type(self):
        try:
            return EventType(self.event_type)
        except ValueError:
            return self.event_type

    def __str__(self):
        return self.payment_id

    def save(self, *args, **kwargs):
        if not self.id:
            signature = get_signature(
                self.event_type, self.webhook_id, self.account_id, self.payment_id, self.raw['created'], self.app_id,
                self.data_id, self.result_status, self.category, self.sub_category, self.response_code,
                self.reconciliation_id, self.amount, self.currency
            )
            if self.signature[len('sig1='):] != signature:
                self.flag = True
                self.flag_code = Flag.INVALID_SIGN
                self.flag_info = 'Invalid signature.'
        super().save(*args, **kwargs)


@receiver(post_save, sender=PaymentsOSNotification)
def payment_notification_save(sender, instance, created, **kwargs):
    if created:
        if instance.is_flagged:
            signals.invalid_notification_received.send(sender=PaymentsOSNotification, instance=instance)
            signals.notification_flagged.send(sender=PaymentsOSNotification, instance=instance)
            return
        else:
            signals.valid_notification_received.send(sender=PaymentsOSNotification, instance=instance)

        if instance.is_event_type_payment_create:
            signals.notification_type_payment_create.send(sender=PaymentsOSNotification, instance=instance)
            return

        if instance.is_event_type_charge_create:
            signals.notification_type_charge_create.send(sender=PaymentsOSNotification, instance=instance)
            if instance.is_result_status_succeed:
                signals.transaction_result_succeed.send(sender=PaymentsOSNotification, instance=instance)
            elif instance.is_result_status_failed:
                signals.transaction_result_failed.send(sender=PaymentsOSNotification, instance=instance)
            elif instance.is_result_status_pending:
                signals.transaction_result_pending.send(sender=PaymentsOSNotification, instance=instance)
