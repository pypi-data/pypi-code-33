from django.http import HttpResponse
from django.views.generic.base import View
from django.views.generic import ListView
from .models import Project


class HealthCheck(View):
    """
    Application health check.

    This view is used by robots to check if the application is in good shape.
    All the necessary backend checks can be implemented here as well.
    """
    http_method_names = ['get']

    def get(self, request):
        return HttpResponse('The application is healthy')


class ProjectListView(ListView):
    model = Project
