from django.apps import AppConfig
from django.db.models.signals import post_delete, post_save


class CampaignsConfig(AppConfig):
    name = 'ccc.marketing.campaigns'
    label = 'ccc_campaigns'

    def ready(self):
        from ccc.marketing.campaigns.signals import post_save_campaign, post_delete_campaign
        from ccc.campaigns.models import Campaign
        post_save.connect(post_save_campaign, sender=Campaign)
        post_delete.connect(post_delete_campaign, sender=Campaign)
