from django.urls import path

from wrd.views import (
    HomeView,
    ApplicationDetail,
    ApplicationList,
    EpisodeDetail,
    DownloadAttachmentView,
    ApplicationEditView,
)

urlpatterns = [
    path("", HomeView.as_view(), name="home"),
    path(
        "application/<int:pk>/", ApplicationDetail.as_view(), name="application-detail"
    ),
    path(
        "application/<int:pk>/edit/",
        ApplicationEditView.as_view(),
        name="application-edit",
    ),
    path("episode/<int:pk>/", EpisodeDetail.as_view(), name="episode-detail"),
    path("applications/", ApplicationList.as_view(), name="application-list"),
    path("dl/<int:pk>/", DownloadAttachmentView.as_view(), name="download-attachment"),
]
