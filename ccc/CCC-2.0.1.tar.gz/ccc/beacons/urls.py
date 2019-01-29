from django.conf.urls import url
from rest_framework.routers import DefaultRouter

from ccc.beacons.api import BeaconViewSet
from ccc.beacons.views import (AnalyticsView, BeaconDetailsView,
                               BeaconLocationView, BillingBeaconsView,
                               BuyBeaconsView, CampaignsFormView,
                               CampaignsView, ContentFormView, ContentsView,
                               DashboardView, DeleteConfirmModalView,
                               DeviceFormView, DevicesView, GroupsView,
                               OrderPreviewBeaconsView, RulesFormView)

router = DefaultRouter()
router.register(r'beacons', BeaconViewSet, base_name='beacons')

urlpatterns = [
    url(r'^buy_beacons/$', BuyBeaconsView.as_view(), name='beacons_buy_beacons'),
    url(r'^(?P<pk>\d+)/billing/$', BillingBeaconsView.as_view(), name='beacons_billing_beacons'),
    url(r'^(?P<pk>\d+)/orderpreview/$', OrderPreviewBeaconsView.as_view(), name='beacons_order_preview'),
    url(r'^device-form/$', DeviceFormView.as_view(), name='beacons_device_form'),
    url(r'^content-form/$', ContentFormView.as_view(), name='beacons_content_form'),
    url(r'^rule-form/$', RulesFormView.as_view(), name='beacons_rule_form'),
    url(r'^campaign-form/$', CampaignsFormView.as_view(), name='beacons_campaign_form'),
    url(r'^delete/$', DeleteConfirmModalView.as_view(), name='beacons_delete'),
    url(r'^dashboard/$', DashboardView.as_view(), name='beacons_dashboard'),
    url(r'^analytics/$', AnalyticsView.as_view(), name='beacons_analytics'),
    url(r'^devices/$', DevicesView.as_view(), name='beacons_devices'),
    url(r'^campaigns/$', CampaignsView.as_view(), name='beacons_campaigns'),
    url(r'^contents/$', ContentsView.as_view(), name='beacons_contents'),
    url(r'^groups/$', GroupsView.as_view(), name='beacons_groups'),
    url(r'^location/$', BeaconLocationView.as_view(), name='beacons_location'),
    url(r'^(?P<pk>\d+)/details/$', BeaconDetailsView.as_view(), name='beacons_details')
]

urlpatterns = urlpatterns + router.urls
