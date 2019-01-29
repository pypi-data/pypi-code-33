from django.apps import AppConfig
from django.db.models.signals import post_save


class FusionutilsConfig(AppConfig):
    name = 'ccsfusion.apps.fusionutils'
    label = 'utils'

    def ready(self):
        from ccsfusion.apps.fusionutils.signals import post_save_form_data
        from srm.apps.form_builders.models import FormDataMapping
        post_save.connect(post_save_form_data, sender=FormDataMapping)
