from django.conf import settings
from edc_model_wrapper import ModelWrapper


class AeTmgModelWrapper(ModelWrapper):

    model = "ambition_ae.aetmg"
    next_url_attrs = ["subject_identifier", "status"]
    next_url_name = settings.DASHBOARD_URL_NAMES.get("tmg_ae_listboard_url")
    querystring_attrs = ["status"]
