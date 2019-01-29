from django.urls import path

from ccc.social_media.facebook.api import views as views

app_name = 'api_facebook'

urlpatterns = [
    path('accounts-connected/', views.SMMFacebookConnectedAccounts.as_view(), name='smm_facebook_accounts_connected_api'),
    path('profile/', views.SMMFacebookGetProfile.as_view(), name='smm_facebook_profile_api'),
    path('logout/', views.FacebookLogout.as_view(), name='smm_logout'),
    path('profile/pages/', views.SMMFacebookGetPages.as_view(),
         name='smm_facebook_pages_api'),
    path('profile/groups/', views.SMMFacebookGetGroups.as_view(),
         name='smm_facebook_groups_api'),
    path('friends/', views.SMMFacebookGetFriends.as_view(), name='smm_facebook_friends_api'),
    path('places/', views.SMMFacebookGetPlaces.as_view(), name='smm_facebook_places_api'),
    path('feeds/<int:id>/', views.SMMFacebookFeeds.as_view(), name='smm_facebook_feeds_api'),
    path('<slug:endpoint>/', views.SMMFacebookGeneric.as_view(), name='smm_facebook_generic_api'),
]
