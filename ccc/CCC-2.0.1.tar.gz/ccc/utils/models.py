from django.conf import settings
from django.db import models

from ccc.campaigns.models import Campaign
from mptt.models import MPTTModel, TreeForeignKey


# TODO #Tech Deb, considering create a "util" package for all packages. So #DRY code.
class DateTimeMixing(models.Model):
    """Date time"""
    is_active = models.BooleanField(default=False)
    update_date = models.DateTimeField(auto_now=True)
    created_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True


class Category(MPTTModel):
    name = models.CharField(max_length=100, unique=True)
    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')

    class MPTTMeta:
        order_insertion_by = ['name']

    def __str__(self):
        return self.name


class CampaignSupplierCategories(DateTimeMixing):
    user = models.ForeignKey(settings.ACCOUNT_USER_PROXY_MODEL, on_delete=models.CASCADE)
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
