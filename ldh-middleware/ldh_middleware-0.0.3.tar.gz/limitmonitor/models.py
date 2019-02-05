from choicesenum import ChoicesEnum
from django.conf import settings
from django.db import models
from django.utils import timezone


class Legacy(ChoicesEnum):
    UNDEFINED = 0, "Undefined"


def create_missing_user_limits(user):

    for code in settings.LM_SERVICES.MAP.keys():
        is_defined = code != settings.LM_SERVICES.UNDEFINED
        is_exists = Limit.objects.filter(user=user, service=code).exists()
        if is_defined and not is_exists:
            Limit(user=user, service=code).save()


def delete_unconverted_user_credits(user):
    identity = user.get_identity()
    ExternalCredit.objects.filter(account_name=identity, is_converted=False).delete()


class Limit(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    service = models.IntegerField(default=settings.LM_SERVICES.UNDEFINED,
                                  choices=settings.LM_SERVICES.choices())
    renewal_date = models.DateTimeField(default=None, blank=True, null=True)
    expiry_date = models.DateTimeField(default=None, blank=True, null=True)
    volume_total = models.DecimalField(default=0, decimal_places=2, max_digits=6)
    time_total = models.DecimalField(default=0, decimal_places=2, max_digits=6)
    is_active = models.BooleanField(default=False)
    created_date = models.DateTimeField(default=timezone.now)
    updated_date = models.DateTimeField(default=timezone.now)

    def service_label(self):

        return settings.LM_SERVICES.get_name_by_code(self.service)

    def active_label(self):

        if self.is_active:
            return "Yes"
        else:
            return "No"

    def endpoint_short_label(self):

        return self.endpoint_label("%Y-%m-%d")

    def endpoint_full_label(self):

        return self.endpoint_label("%Y-%m-%d %H:%M:%S %z")

    def endpoint_label(self, label_format):

        is_blank = self.renewal_date is None and self.expiry_date is None
        is_renewal = self.renewal_date is not None and self.expiry_date is None
        is_expiry = self.renewal_date is None and self.expiry_date is not None

        if is_blank:
            return "-"
        elif is_renewal:
            return self.renewal_date.strftime(label_format)
        elif is_expiry:
            return self.expiry_date.strftime(label_format)
        else:
            return "Invalid"

    def credit_label(self):

        if self.service == settings.LM_SERVICES.TUNNEL:
            return self.days_credit_label()
        else:
            return self.days_credit_label()

    def timedelta_to_daystring(self, delta):

        single_day = 60 * 60 * 24
        days = int(round(delta.total_seconds() / single_day))

        if days <= 62:
            return str(days) + " days"
        elif days <= 744:
            return str(days // 30) + " months"
        else:
            return str(days // 365) + " years"

    def days_credit_label(self):

        has_zero = self.expiry_date is None and self.renewal_date is None and self.time_total == 0
        has_credit_only = self.expiry_date is None and self.renewal_date is None and self.time_total > 0
        has_valid_expiry = self.expiry_date is not None and self.renewal_date is None and self.time_total == 0
        has_valid_renewal = self.expiry_date is None and self.renewal_date is not None and self.time_total == 0

        if has_zero:
            label = "-"
        elif has_credit_only:
            label = str(int(self.time_total)) + " days"
        elif has_valid_expiry:
            difference = self.expiry_date - timezone.now()
            label = self.timedelta_to_daystring(difference)
        elif has_valid_renewal:
            difference = self.renewal_date - timezone.now()
            label = self.timedelta_to_daystring(difference)
        else:
            label = "Invalid"

        return label


class ExternalBundle(models.Model):
    parser = models.IntegerField(default=settings.LM_PARSERS.UNDEFINED,
                                 choices=settings.LM_PARSERS.choices())
    external_key = models.CharField(max_length=30)
    service = models.IntegerField(default=settings.LM_SERVICES.UNDEFINED,
                                  choices=settings.LM_SERVICES.choices())
    time_credit = models.DecimalField(default=0, decimal_places=2, max_digits=6)
    volume_credit = models.DecimalField(default=0, decimal_places=2, max_digits=6)
    created_date = models.DateTimeField(default=timezone.now)
    updated_date = models.DateTimeField(default=timezone.now)


class ExternalCredit(models.Model):
    parser = models.IntegerField(default=settings.LM_PARSERS.UNDEFINED,
                                 choices=settings.LM_PARSERS.choices())
    external_key = models.CharField(max_length=30)
    label = models.CharField(max_length=30)
    bundle_key = models.CharField(max_length=30)
    bundle_label = models.CharField(max_length=30)
    quantity = models.DecimalField(default=1, decimal_places=2, max_digits=6)
    account_name = models.CharField(max_length=30, default="")
    additional_data = models.TextField(default="")
    error_message = models.TextField(default="")
    is_converted = models.BooleanField(default=False)
    created_date = models.DateTimeField(default=timezone.now)
    updated_date = models.DateTimeField(default=timezone.now)

    @property
    def parser_name(self):
        return settings.LM_PARSERS.get_name_by_code(self.parser)

    @property
    def external_code(self):
        return self.parser_name + ":" + str(self.external_key)

    @property
    def external_bundle(self):
        return self.parser_name + ":" + str(self.external_key)


class Credit(models.Model):
    limit = models.ForeignKey(Limit)
    external = models.ForeignKey(ExternalCredit, blank=True, null=True, default=None)
    time_credit = models.DecimalField(default=0, decimal_places=2, max_digits=6)
    volume_credit = models.DecimalField(default=0, decimal_places=2, max_digits=6)
    old_expiry_date = models.DateTimeField(blank=True, null=True, default=None)
    old_time_total = models.DecimalField(blank=True, null=True, default=None, decimal_places=2, max_digits=6)
    old_volume_total = models.DecimalField(blank=True, null=True, default=None, decimal_places=2, max_digits=6)
    new_expiry_date = models.DateTimeField(blank=True, null=True, default=None)
    new_time_total = models.DecimalField(blank=True, null=True, default=None, decimal_places=2, max_digits=6)
    new_volume_total = models.DecimalField(blank=True, null=True, default=None, decimal_places=2, max_digits=6)
    created_date = models.DateTimeField(default=timezone.now)
    updated_date = models.DateTimeField(default=timezone.now)
