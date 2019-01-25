from django.urls import path, include
from rest_framework import routers

from . import api
from . import views

router = routers.DefaultRouter()
router.register(r'project', api.ProjectViewSet)
router.register(r'projectmetadata', api.ProjectMetadataViewSet)
router.register(r'experiment', api.ExperimentViewSet)
router.register(r'experimentmetadata', api.ExperimentMetadataViewSet)
router.register(r'sample', api.SampleViewSet)
router.register(r'samplemetadata', api.SampleMetadataViewSet)
router.register(r'condition', api.ConditionViewSet)
router.register(r'conditiontadata', api.ConditionMetadataViewSet)

urlpatterns = (
    # urls for Django Rest Framework API
    path('api/v1/', include(router.urls)),
)

urlpatterns += (
    # urls for Project
    path('health/', views.HealthCheck.as_view(), name='health'),
    path('project/', views.ProjectListView.as_view(), name='project_list'),
)
