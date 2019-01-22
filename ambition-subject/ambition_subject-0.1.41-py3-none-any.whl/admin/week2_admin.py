from django.contrib import admin
from edc_model_admin import TabularInlineMixin
from edc_model_admin import audit_fieldset_tuple

from ..admin_site import ambition_subject_admin
from ..forms import AmphotericinMissedDosesForm
from ..forms import FluconazoleMissedDosesForm
from ..forms import FlucytosineMissedDosesForm
from ..forms import SignificantDiagnosesForm
from ..forms import Week2Form
from ..models import SignificantDiagnoses, FlucytosineMissedDoses
from ..models import Week2, FluconazoleMissedDoses, AmphotericinMissedDoses
from .modeladmin_mixins import CrfModelAdminMixin
from ambition_lists.models import OtherDrug, Day14Medication
from edc_constants.constants import NOT_APPLICABLE


class SignificantDiagnosesInline(TabularInlineMixin, admin.TabularInline):

    model = SignificantDiagnoses
    form = SignificantDiagnosesForm
    extra = 1

    fieldsets = (
        ['Admission history', {
            'fields': (
                'possible_diagnoses',
                'dx_date',
                'dx_other')},
         ],)


class AmphotericinMissedDosesInline(TabularInlineMixin, admin.TabularInline):

    model = AmphotericinMissedDoses
    form = AmphotericinMissedDosesForm
    extra = 1

    fieldsets = (
        ['Admission history', {
            'fields': (
                'day_missed',
                'missed_reason',
                'missed_reason_other')},
         ],)


class FluconazoleMissedDosesInline(TabularInlineMixin, admin.TabularInline):

    model = FluconazoleMissedDoses
    form = FluconazoleMissedDosesForm
    extra = 1

    fieldsets = (
        ['Admission history', {
            'fields': (
                'day_missed',
                'missed_reason',
                'missed_reason_other')},
         ],)


class FlucytosineMissedDosesInline(TabularInlineMixin, admin.TabularInline):

    model = FlucytosineMissedDoses
    form = FlucytosineMissedDosesForm
    extra = 1

    fieldsets = (
        ['Admission history', {
            'fields': (
                'day_missed',
                'doses_missed',
                'missed_reason',
                'missed_reason_other')},
         ],)


@admin.register(Week2, site=ambition_subject_admin)
class Week2Admin(CrfModelAdminMixin, admin.ModelAdmin):

    form = Week2Form

    inlines = [SignificantDiagnosesInline, FluconazoleMissedDosesInline,
               AmphotericinMissedDosesInline, FlucytosineMissedDosesInline]

    fieldsets = (
        ['Part1: Admission history', {
            'fields': (
                'subject_visit',
                'report_datetime',
                'discharged',
                'discharge_date',
                'research_discharge_date',
                'died',
                'death_date_time')},
         ],
        ['Part2: Induction phase study medication', {
            'fields': (
                'ampho_start_date',
                'ampho_end_date',
                'flucon_start_date',
                'flucon_stop_date',
                'flucy_start_date',
                'flucy_stop_date',
                'ambi_start_date',
                'ambi_stop_date',
                'drug_intervention',
                'drug_intervention_other',
                'antibiotic',
                'antibiotic_other',
                'blood_received',
                'units')}
         ],
        ['Part3: Clinical assessment', {
            'fields': (
                'headache',
                'glasgow_coma_score',
                'confusion',
                'recent_seizure_less_72',
                'cn_palsy',
                'behaviour_change',
                'focal_neurology',
                'weight',
                'medicines',
                'medicine_other',
                'other_significant_dx'
            )}
         ],
        audit_fieldset_tuple
    )

    radio_fields = {
        'discharged': admin.VERTICAL,
        'died': admin.VERTICAL,
        'flucon_missed_doses': admin.VERTICAL,
        'amphotericin_missed_doses': admin.VERTICAL,
        'blood_received': admin.VERTICAL,
        'headache': admin.VERTICAL,
        'recent_seizure_less_72': admin.VERTICAL,
        'behaviour_change': admin.VERTICAL,
        'confusion': admin.VERTICAL,
        'cn_palsy': admin.VERTICAL,
        'focal_neurology': admin.VERTICAL,
        'other_significant_dx': admin.VERTICAL
    }

    filter_horizontal = ('antibiotic', 'medicines', 'drug_intervention')

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == "drug_intervention":
            kwargs["queryset"] = OtherDrug.objects.exclude(
                short_name=NOT_APPLICABLE).order_by('display_index')
        if db_field.name == "medicines":
            kwargs["queryset"] = Day14Medication.objects.exclude(
                short_name=NOT_APPLICABLE).order_by('display_index')
        return super().formfield_for_manytomany(db_field, request, **kwargs)
