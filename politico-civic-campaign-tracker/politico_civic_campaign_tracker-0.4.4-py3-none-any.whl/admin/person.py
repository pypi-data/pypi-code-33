import nested_admin

from biography.models import (
    Biography,
    Birthplace,
    Education,
    Financials,
    Ideology,
    Legislation,
    Occupation,
    PastCampaign,
    Publication,
    Residence,
)
from campaign.models import Campaign
from election.models import Candidate
from tracker.models import CampaignContent


class CampaignContentInline(nested_admin.NestedStackedInline):
    model = CampaignContent


class CampaignAdmin(nested_admin.NestedStackedInline):
    model = Campaign
    inlines = [CampaignContentInline]
    verbose_name_plural = "Campaign"


class CandidateAdmin(nested_admin.NestedStackedInline):
    model = Candidate
    inlines = [CampaignAdmin]
    verbose_name = "Candidacy"
    verbose_name_plural = "Candidacy"
    extra = 0


class BirthplaceInline(nested_admin.NestedTabularInline):
    model = Birthplace


class FinancialsInline(nested_admin.NestedTabularInline):
    model = Financials


class IdeologyInline(nested_admin.NestedTabularInline):
    model = Ideology


class EducationInline(nested_admin.NestedStackedInline):
    model = Education
    verbose_name = "Educational Accomplishment"
    extra = 0


class OccupationInline(nested_admin.NestedStackedInline):
    model = Occupation
    extra = 0


class PastCampaignInline(nested_admin.NestedStackedInline):
    model = PastCampaign
    autocomplete_fields = ["office"]
    extra = 0


class PublicationInline(nested_admin.NestedStackedInline):
    model = Publication
    extra = 0


class LegislationInline(nested_admin.NestedStackedInline):
    model = Legislation
    verbose_name = "Legislative Accomplishment"
    extra = 0


class ResidenceInline(nested_admin.NestedTabularInline):
    model = Residence


class BiographyAdmin(nested_admin.NestedStackedInline):
    model = Biography
    inlines = [
        BirthplaceInline,
        ResidenceInline,
        EducationInline,
        OccupationInline,
        PastCampaignInline,
        IdeologyInline,
        LegislationInline,
        FinancialsInline,
        PublicationInline,
    ]
    exclude = ["notes"]
    verbose_name_plural = "Biography"


class PersonAdmin(nested_admin.NestedModelAdmin):
    inlines = [BiographyAdmin, CandidateAdmin]
    search_fields = ["full_name"]
    ordering = ["last_name"]
    fields = [
        "last_name",
        "first_name",
        "middle_name",
        "full_name",
        "gender",
        "race",
        "nationality",
        "birth_date",
        "summary",
    ]

    def save_model(self, request, obj, form, change):
        if not obj.pk:  # call super method if object has no primary key
            super(PersonAdmin, self).save_model(request, obj, form, change)
        else:
            pass  # don't actually save the parent instance

    def save_related(self, request, form, formsets, change):
        form.save_m2m()
        for formset in formsets:
            self.save_formset(request, form, formset, change=change)
        super(PersonAdmin, self).save_model(
            request, form.instance, form, change
        )

    class Media:
        css = {"all": ("css/admin/changes.css",)}
