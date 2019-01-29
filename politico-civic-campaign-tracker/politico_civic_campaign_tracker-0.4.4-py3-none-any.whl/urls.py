from django.urls import path, re_path

from .views import (
    CandidateAPI,
    CandidateRatingsAPI,
    EndorsementAPI,
    QuoteAPI,
    RatingsAPI,
    StoryAPI,
    TweetAPI,
    VideoAPI,
    RankingSetsAdmin,
    RankingsAdmin,
)
from .viewsets import (
    PersonList,
    PersonDetail,
    CandidateRatingCategoryList,
    CandidateRatingCategoryDetail,
    RankingSetAdminView,
    RankingsAdminView,
)


urlpatterns = [
    path("rankings/", RankingSetsAdmin.as_view(), name=RankingSetsAdmin.name),
    path("rankings/new", RankingsAdmin.as_view(), name=RankingsAdmin.name),
    re_path(
        r"^rankings/(?P<pk>.+)/$",
        RankingsAdmin.as_view(),
        name=RankingsAdmin.name,
    ),
    path("api/people/", PersonList.as_view(), name="tracker_api_person-list"),
    re_path(
        r"^api/people/(?P<pk>.+)/$",
        PersonDetail.as_view(),
        name="tracker_api_person-detail",
    ),
    path(
        "api/categories/",
        CandidateRatingCategoryList.as_view(),
        name="tracker_api_rating-category-list",
    ),
    re_path(
        r"^api/categories/(?P<pk>.+)/$",
        CandidateRatingCategoryDetail.as_view(),
        name="tracker_api_rating-category-detail",
    ),
    path("api/candidates/", CandidateAPI.as_view()),
    path("api/candidate-ratings/", CandidateRatingsAPI.as_view()),
    path("api/endorsements/", EndorsementAPI.as_view()),
    path("api/quotes/", QuoteAPI.as_view()),
    path("api/ratings/", RatingsAPI.as_view()),
    path("api/stories/", StoryAPI.as_view()),
    path("api/tweets/", TweetAPI.as_view()),
    path("api/videos/", VideoAPI.as_view()),
    path("api/ranking-sets/", RankingSetAdminView.as_view()),
    path("api/ranking-sets/new/", RankingsAdminView.as_view()),
    re_path(r"^api/ranking-sets/(?P<pk>.+)/$", RankingsAdminView.as_view()),
]
