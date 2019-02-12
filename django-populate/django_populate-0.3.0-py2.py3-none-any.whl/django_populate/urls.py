from django.urls import path
from django.views.generic import TemplateView

urlpatterns = [
    path('preview.html', TemplateView.as_view(template_name='faker/preview.html'))
]
