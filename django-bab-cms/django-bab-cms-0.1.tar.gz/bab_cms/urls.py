from django.urls import path

from .views import *

urlpatterns = [
    path('articles/', ArticleListView.as_view(), name='cms-article-list'),
    path('articles/<slug:category_slug>/', ArticleListView.as_view(), name='cms-article-list'),
    path('article/<slug:slug>/', ArticleDetail.as_view(), name='cms-article-detail'),
    #
    path('posts/', PostListView.as_view(), name='cms-post-list'),
    path('posts/<slug:category_slug>/', PostListView.as_view(), name='cms-post-list'),
    path('post/<slug:slug>/', PostDetail.as_view(), name='cms-post-detail'),
    #
    # path('categories/', CategoryList.as_view(), name='cms-category-list'),
    path('categorie/<slug:slug>', CategoryDetailView.as_view(), name='cms-category-detail')
]
