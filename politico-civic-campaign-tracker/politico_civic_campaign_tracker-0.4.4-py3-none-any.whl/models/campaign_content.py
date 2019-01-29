from django.db import models
from campaign.models import Campaign


class CampaignContent(models.Model):
    """
    Content related to a campaign.
    """

    campaign = models.OneToOneField(
        Campaign, related_name="content", on_delete=models.PROTECT
    )
    blurb = models.TextField()
