import logging

from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from ccc.contacts.api.serializers import ContactSerializer
from ccc.contacts.cloud_tasks import (create_supplier_by_contact,
                                      send_business_card_url_task)
from ccc.contacts.elasticsearch import ContactElasticSearch
from ccc.contacts.models import Contact

logger = logging.getLogger(__name__)


def contact_as_supplier(contact_instace, **kwargs):
    create_supplier_by_contact(contact_id=contact_instace.id).execute()
    logger.info('Supplier is created by contact id {}'.format(contact_instace.id))


def send_business_card_url(contact_instace, **kwargs):
    send_business_card_url_task(contact_id=contact_instace.id).execute()
    logger.info('Digital Business Card created for contact id {}'.format(contact_instace.id))


@receiver(post_save, sender=Contact)
def post_save_contact(sender, instance, **kwargs):
    if kwargs.get('created'):
        if instance.is_supplier:
            contact_as_supplier(instance, **kwargs)
        if instance.contact_type == 'DBC' and instance.source == 'M':
            send_business_card_url(instance, **kwargs)
    try:
        ce = ContactElasticSearch()
        ce.store_record(id=instance.id, data=ContactSerializer(instance).data)
    except Exception as ex:
        logger.info('Contact data is not saved in elastic search index for contact id {},'
                    '{}'.format(instance.id, ex))


@receiver(post_delete, sender=Contact)
def post_delete_contact(sender, instance, **kwargs):
    try:
        ce = ContactElasticSearch()
        ce.delete_record(id=instance.id)
    except Exception as ex:
        logger.info('Contact data is not deleted in elastic search index for contact id {},'
                    '{}'.format(instance.id, ex))
