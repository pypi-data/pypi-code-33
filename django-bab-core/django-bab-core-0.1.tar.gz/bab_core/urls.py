
from django.conf import settings
from django.urls import path, include
from django.views.generic import TemplateView
from .views import index, update_profile, contact

urlpatterns = [
    path('', index, name='core-index'),
    path('contact/', contact, name='core-contact'),
    path('maintenance/', TemplateView.as_view(template_name='site/maintenance.html'), name='core-maintenance'),
    path('accounts/profile', update_profile, name='accounts-profile')
]
