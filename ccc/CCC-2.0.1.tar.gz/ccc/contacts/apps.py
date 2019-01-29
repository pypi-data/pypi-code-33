from django.apps import AppConfig
from django.db.models.signals import post_delete, post_save


class ContactsConfig(AppConfig):
    name = 'ccc.contacts'
    label = 'crm_contacts'

    def ready(self):
        from ccc.contacts.signals import post_save_contact, post_delete_contact
        from ccc.contacts.models import Contact
        post_save.connect(post_save_contact, sender=Contact)
        post_delete.connect(post_delete_contact, sender=Contact)
