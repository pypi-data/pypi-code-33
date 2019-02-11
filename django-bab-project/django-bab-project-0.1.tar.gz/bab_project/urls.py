from django.urls import path

from .views import *

urlpatterns = [
    path('', ProjectListView.as_view(), name='project-project-list'),
    path('<slug:category>', ProjectListView.as_view(), name='project-project-list'),
    path('<slug:slug>/', ProjectDetailView.as_view(), name='project-project-detail'),
    path('categorie/<slug:slug>', CategoryDetailView.as_view(), name='project-category-detail')

]
