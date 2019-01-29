from django.contrib import admin

from ccsfusion.apps.fusionutils.models import CampaignSupplierCategories


class CampaignSupplierCategoriesAdmin(admin.ModelAdmin):
    list_display = ('user', 'campaign__name', 'category', 'is_active')

    @staticmethod
    def campaign__name(obj):
        return obj.campaign.name


admin.site.register(CampaignSupplierCategories, CampaignSupplierCategoriesAdmin)
