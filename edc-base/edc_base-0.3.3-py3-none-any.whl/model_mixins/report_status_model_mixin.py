from django.db import models
# from edc_constants.constants import CLOSED, OPEN

from ..choices import REPORT_STATUS
from ..model_validators.date import datetime_not_future


class ReportStatusModelMixin(models.Model):

    report_status = models.CharField(
        verbose_name='What is the status of this report?',
        max_length=25,
        choices=REPORT_STATUS)

    report_closed_datetime = models.DateTimeField(
        blank=True,
        null=True,
        validators=[datetime_not_future],
        verbose_name=('Date and time report closed.'))

#     @property
#     def status(self):
#         if self.report_status == CLOSED:
#             return 'Closed'
#         elif self.report_status == OPEN:
#             return 'Open'
#         else:
#             return self.report_status

    class Meta:
        abstract = True
