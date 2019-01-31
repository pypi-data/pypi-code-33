from django.views.generic import TemplateView, DetailView, ListView
from system.models import Links


class QtTemplateView(TemplateView):
    def dispatch(self, request, *args, **kwargs):
        self.template_name = request.template + '/' + self.template_name
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['links'] = Links.objects.filter(site=self.request.site).all()
        return context


class QtDetailView(DetailView):
    def dispatch(self, request, *args, **kwargs):
        self.template_name = request.template + '/' + self.template_name
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['links'] = Links.objects.filter(site=self.request.site).all()
        return context


class QtListView(ListView):
    def dispatch(self, request, *args, **kwargs):
        self.template_name = request.template + '/' + self.template_name
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=object_list, **kwargs)
        context['links'] = Links.objects.filter(site=self.request.site).all()
        return context
