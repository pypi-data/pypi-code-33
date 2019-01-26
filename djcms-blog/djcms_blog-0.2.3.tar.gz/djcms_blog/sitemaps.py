from django.contrib.sitemaps import Sitemap

from .models import PostTitle


class PostsSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.5

    def items(self):
        return PostTitle.objects.filter(is_draft=False, published=True)

    def lastmod(self, obj):
        return obj.published_date
