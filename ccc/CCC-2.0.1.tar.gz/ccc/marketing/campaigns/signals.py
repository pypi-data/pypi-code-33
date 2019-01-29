import logging

from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from ccc.campaigns.models import Campaign
from ccc.marketing.campaigns.api.serializers import CampaignSerializer
from ccc.marketing.campaigns.elasticsearch import CampaignElasticSearch

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Campaign)
def post_save_campaign(sender, instance, **kwargs):
    try:
        ce = CampaignElasticSearch()
        ce.store_record(id=instance.id, data=CampaignSerializer(instance).data)
    except Exception as ex:
        logger.info('Campaign data is not saved in elastic search index for campaign id {},'
                    '{}'.format(instance.id, ex))


@receiver(post_delete, sender=Campaign)
def post_delete_campaign(sender, instance, **kwargs):
    try:
        ce = CampaignElasticSearch()
        ce.delete_record(id=instance.id)
    except Exception as ex:
        logger.info('Campaign data is not deleted in elastic search index for contact id {},'
                    '{}'.format(instance.id, ex))
