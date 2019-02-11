from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView

from .models import Category, Article, Post, Publishable


class PublicationListView(ListView):
    paginate_by = 5
    template_name = 'bab_cms/publishable_list.html'
    ordering = ['-published_at']

    def get_queryset(self):
        return self.model.published.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if self.model == Article:
            context['header_title'] = 'Les Articles'
            context['header_text'] = 'Articles / Tutos...'

        elif self.model == Post:
            context['header_title'] = 'Les Nouvelles'
            context['header_text'] = ''

        return context


class ArticleListView(PublicationListView):
    model = Article


class PostListView(PublicationListView):
    model = Post


class ArticleDetail(DetailView):
    model = Article

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['summary'] = self.object.get_root().get_descendants(include_self=True)
        return context


class PostDetail(DetailView):
    model = Post


class CategoryDetailView(DetailView):
    model = Category

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['header_title'] = 'Catégorie'
        context['header_text'] = self.object
        return context


