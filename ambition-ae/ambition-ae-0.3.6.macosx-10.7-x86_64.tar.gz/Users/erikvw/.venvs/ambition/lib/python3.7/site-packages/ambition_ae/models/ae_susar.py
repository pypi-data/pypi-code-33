# from django.db import models
# from edc_action_item.models import ActionModelMixin
# from edc_base.model_mixins import BaseUuidModel
# from edc_base.sites import SiteModelMixin
# from edc_constants.choices import YES_NO
# from edc_identifier.model_mixins import TrackingModelMixin
#
# from ..constants import AE_SUSAR_ACTION
#
#
# class AeSusar(ActionModelMixin, TrackingModelMixin,
#               SiteModelMixin, BaseUuidModel):
#
#     tracking_identifier_prefix = 'AS'
#
#     action_name = AE_SUSAR_ACTION
#
#     report_submitted = models.CharField(
#         max_length=15,
#         choices=YES_NO)
#
#     date_submitted = models.DateField()
#
#     class Meta:
#         verbose_name = 'AE SUSAR Report'
