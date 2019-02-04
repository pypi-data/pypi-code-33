from django.urls import path, include
from rest_framework import routers

from . import api
from . import views

router = routers.DefaultRouter()
router.register(r'computationaltool', api.ComputationalToolViewSet)
router.register(r'computationalwf', api.ComputationalWFViewSet)

urlpatterns = (
    # urls for Django Rest Framework API
    path('api/v1/', include(router.urls)),
)

urlpatterns += (
    # urls for Chromosome
    path('health/', views.HealthCheck.as_view(), name='health'),
)
