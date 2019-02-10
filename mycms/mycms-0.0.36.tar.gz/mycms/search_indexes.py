
import datetime
from haystack import indexes
from mycms.models import CMSEntries

class CMSEntriesIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    author = indexes.CharField(model_attr='created_by')
    pub_date = indexes.DateTimeField(model_attr='date_modified')

    def get_model(self):
        return CMSEntries

    def index_queryset(self, using=None):
        return self.get_model().objects.filter(published=True)


