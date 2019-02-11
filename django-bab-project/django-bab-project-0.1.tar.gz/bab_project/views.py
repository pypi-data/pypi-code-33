from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView

from .models import Project, Category


class ProjectListView(ListView):
    model = Project

    def get_queryset(self):
        if 'category' in self.kwargs:
            category = get_object_or_404(Category.objects.filter(slug=self.kwargs['category']))
            return Project.objects.filter(category=category)
        else:
            return super(ProjectListView, self).get_queryset()


class ProjectDetailView(DetailView):
    model = Project

class CategoryDetailView(DetailView):
    model = Category

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['header_title'] = 'Catégorie'
        context['header_text'] = self.object
        return context