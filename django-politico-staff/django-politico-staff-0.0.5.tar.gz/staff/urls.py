
from django.urls import include, path
from rest_framework import routers

from .views import EditProfile, PatchProfile, SyncUser
from .viewsets import StafferViewSet

router = routers.DefaultRouter()

router.register(r"staffer", StafferViewSet, basename="staffer")

urlpatterns = [
    path("api/", include(router.urls)),
    path("edit-profile/", EditProfile.as_view(), name="staff-edit-profile"),
    path("sync-profile/", SyncUser.as_view(), name="staff-sync-profile"),
    path("patch-profile/", PatchProfile.as_view(), name="staff-patch-profile"),
]
