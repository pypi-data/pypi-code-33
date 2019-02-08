from django.contrib import admin
from edc_action_item import action_fieldset_tuple
from edc_model_admin import audit_fieldset_tuple

from ..admin_site import ambition_ae_admin
from ..forms import AeSusarForm
from ..models import AeSusar
from .modeladmin_mixins import ModelAdminMixin, NonAeInitialModelAdminMixin


@admin.register(AeSusar, site=ambition_ae_admin)
class AeSusarAdmin(ModelAdminMixin, NonAeInitialModelAdminMixin, admin.ModelAdmin):

    form = AeSusarForm

    # additional_instructions = "For completion by TMG Investigators Only"
    subject_dashboard_url = "susar_ae_listboard_url"

    list_display = [
        "subject_identifier",
        "dashboard",
        "status",
        "ae_initial",
        "report_datetime",
        "submitted_datetime",
    ]

    list_filter = ("report_status", "report_datetime", "submitted_datetime")

    search_fields = [
        "subject_identifier",
        "action_identifier",
        "ae_initial__action_identifier",
        "ae_initial__tracking_identifier",
        "tracking_identifier",
    ]

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "subject_identifier",
                    "ae_initial",
                    "report_datetime",
                    "submitted_datetime",
                    "report_status",
                )
            },
        ),
        action_fieldset_tuple,
        audit_fieldset_tuple,
    )

    radio_fields = {"report_status": admin.VERTICAL}

    def status(self, obj=None):
        return obj.report_status.title()
