from django.urls import path

from ccc.marketing.campaigns.views import (ActiveCampaignsView,
                                           CampaignLogTypesView,
                                           CampaignsKeywordsView,
                                           CampaignsView, CampaignTypesView,
                                           EditCampaignsView,
                                           EditFollowUPCampaignsView,
                                           FollowUpCampaignsView,
                                           FollowUPCampaignsView)

app_name = 'campaigns'

urlpatterns = [
    path('', ActiveCampaignsView.as_view(), name='list_campaigns'),
    path('<int:campaign_id>/edit/', EditCampaignsView.as_view(), name='edit_campaign'),
    path('create/', CampaignsView.as_view(), name='create_campaign'),
    path('keywords/', CampaignsKeywordsView.as_view(), name='campaign-keywords'),
    path('follow-ups/', FollowUpCampaignsView.as_view(), name='follow-ups-campaigns'),
    path('<int:campaign_id>/follow-up/', FollowUPCampaignsView.as_view(), name='create_fu_campaigns'),
    path('<int:campaign_id>/follow-up/edit/', EditFollowUPCampaignsView.as_view(),
         name='edit_fu_campaigns'),
    path('<str:campaign_type>/', CampaignTypesView.as_view(), name='campaign-types'),
    path('<str:campaign_type>/<str:campaign_direction>/', CampaignLogTypesView.as_view(),
         name='campaign-log-types'),

]
