from django.urls import path

from ccc.social_media.facebook.api.views import (SMMFacebookConnectedAccounts,
                                                 SMMFacebookFeeds)
from ccc.social_media.social.api import views as views

app_name = 'api_social'

urlpatterns = [
    path('post/', views.ListPostsLocal.as_view(), name='smm_social_pending_post_local'),
    path('post/facebook/create', views.CreateFacebookPost.as_view(), name='smm_social_create_post_facebook'),
    path('post/facebook/list/<int:id>/', SMMFacebookFeeds.as_view(), name='smm_social_list_posts_facebook'),
    path('accounts/facebook/', SMMFacebookConnectedAccounts.as_view(), name='smm_social_list_connected_facebook')
]
