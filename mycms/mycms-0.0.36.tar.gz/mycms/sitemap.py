from django.contrib.sitemaps import Sitemap
from . models import CMSEntries

class CMSEntriesSiteMap(Sitemap):
    
    changefreq = "weekly"
    priority = 0.7

    def items(self):
        return CMSEntries.objects.filter(published=True)
 
    def lastmod(self, item): 
        return item.date_modified
