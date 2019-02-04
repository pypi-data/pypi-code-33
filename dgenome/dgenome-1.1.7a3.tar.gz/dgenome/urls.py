from django.urls import path, include
from rest_framework import routers

from . import api
from dgenome.views import HealthCheck

router = routers.DefaultRouter()
router.register(r'genome', api.GenomeViewSet)
router.register(r'chromosome', api.ChromosomeViewSet)
router.register(r'gene', api.GeneViewSet)
router.register(r'transcript', api.TranscriptViewSet)

urlpatterns = (
    # urls for Django Rest Framework API
    path('api/v1/', include(router.urls)),
)

urlpatterns += (
    # urls for Chromosome
    path('health/', HealthCheck.as_view(), name='health'),
)
