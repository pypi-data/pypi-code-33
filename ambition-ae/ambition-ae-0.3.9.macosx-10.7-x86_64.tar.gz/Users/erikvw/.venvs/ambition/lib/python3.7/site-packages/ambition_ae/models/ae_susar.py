from django.db import models
from django.db.models.deletion import PROTECT
from edc_action_item.managers import (
    ActionIdentifierSiteManager,
    ActionIdentifierManager,
)
from edc_action_item.models import ActionModelMixin
from edc_base.model_mixins import BaseUuidModel, ReportStatusModelMixin
from edc_base.model_validators.date import datetime_not_future
from edc_base.sites import SiteModelMixin
from edc_base.utils import get_utcnow
from edc_identifier.model_mixins import TrackingModelMixin

from ..constants import AE_SUSAR_ACTION
from .ae_initial import AeInitial


class AeSusar(
    ActionModelMixin,
    TrackingModelMixin,
    ReportStatusModelMixin,
    SiteModelMixin,
    BaseUuidModel,
):

    action_name = AE_SUSAR_ACTION

    tracking_identifier_prefix = "AS"

    ae_initial = models.ForeignKey(AeInitial, on_delete=PROTECT)

    report_datetime = models.DateTimeField(
        verbose_name="Report date and time",
        validators=[datetime_not_future],
        default=get_utcnow,
    )

    submitted_datetime = models.DateTimeField(
        verbose_name="AE SUSAR submitted on",
        validators=[datetime_not_future],
        null=True,
        blank=True,
    )

    on_site = ActionIdentifierSiteManager()

    objects = ActionIdentifierManager()

    def __str__(self):
        return f"{self.action_identifier[-9:]}"

    def save(self, *args, **kwargs):
        self.subject_identifier = self.ae_initial.subject_identifier
        super().save(*args, **kwargs)

    def natural_key(self):
        return (self.action_identifier,)

    def get_search_slug_fields(self):
        fields = super().get_search_slug_fields()
        fields.append("subject_identifier")
        fields.append("report_status")
        return fields

    class Meta:
        verbose_name = "AE SUSAR Report"
