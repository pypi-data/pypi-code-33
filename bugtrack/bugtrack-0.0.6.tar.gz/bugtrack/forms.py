from django.db.models import Case, When
from generalobj.forms import GeneralObjForm

from .models import Bug, Category


class BugForm(GeneralObjForm):
    def __init__(self, *args, **kwargs):
        super(BugForm, self).__init__(*args, **kwargs)
        top_categories = Category.objects.filter(parent__isnull=True)
        categories = []
        #Widget vagy hasonlo attributhoz onclick onload szeru dolgot beallitani,
        #hogy ujratoltse kattintasnal (ha van meg gyerek), es arra menjen.
        #Nyilvan csak a selectet toltse ujra.
        for top_category in top_categories:
            categories.append(top_category)
            categories.extend(top_category.get_children_tree())
        ids = [cat.id for cat in categories \
                if cat.has_access(self.request.user)]
        preserved = Case(*[When(pk=pk, then=pos) for pos, pk in enumerate(ids)])
        self.fields['category'].queryset = Category.objects.filter(id__in=ids).\
                order_by(preserved)

    class Meta:
        model = Bug
        fields = ('category', 'priority', 'severity', 'assigned_to', \
                'subject', 'text', 'executor', 'tester', 'parent', 'depends_on')