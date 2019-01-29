import simplejson as json
from django.conf import settings
from django.views.generic.base import TemplateView

from ccc.common.mixins import LoginRequiredMixin


class BuyBeaconsView(LoginRequiredMixin, TemplateView):
    """Beacons buy tempate"""
    template_name = 'ccc/beacons/buy_beacons/buy_beacons.html'


class BillingBeaconsView(LoginRequiredMixin, TemplateView):
    """Beacons billing page"""
    template_name = 'ccc/beacons/buy_beacons/billing_beacons.html'


class OrderPreviewBeaconsView(LoginRequiredMixin, TemplateView):
    """Beacons order preview Page"""
    template_name = 'ccc/beacons/buy_beacons/order_preview.html'


class DashboardView(LoginRequiredMixin, TemplateView):
    """Beacons Dashboard"""
    template_name = 'ccc/beacons/dashboard.html'


class AnalyticsView(LoginRequiredMixin, TemplateView):
    """Beacons Analytics"""
    template_name = 'ccc/beacons/analytics.html'


class DevicesView(LoginRequiredMixin, TemplateView):
    """Beacons Devices"""
    template_name = 'ccc/beacons/devices/devices.html'


class CampaignsView(LoginRequiredMixin, TemplateView):
    """Beacons Campaigns"""
    template_name = 'ccc/beacons/campaigns/campaigns.html'


class CampaignsFormView(LoginRequiredMixin, TemplateView):
    """Beacons Campaigns form"""
    template_name = 'ccc/beacons/campaigns/campaign_form.html'


class RulesFormView(LoginRequiredMixin, TemplateView):
    """Beacons Rules form"""
    template_name = 'ccc/beacons/campaigns/rules_form.html'


class ContentsView(LoginRequiredMixin, TemplateView):
    """Beacons Contents"""
    template_name = 'ccc/beacons/contents/contents.html'


class GroupsView(LoginRequiredMixin, TemplateView):
    """Beacons Groups"""
    template_name = 'ccc/beacons/groups.html'


class BeaconDetailsView(LoginRequiredMixin, TemplateView):
    """Beacons Details"""
    template_name = 'ccc/beacons/details.html'


class BeaconLocationView(LoginRequiredMixin, TemplateView):
    """Beacons location Details"""
    template_name = 'ccc/beacons/devices/location.html'

    def get_context_data(self, **kwargs):
        kwargs = super(BeaconLocationView, self).get_context_data(**kwargs)
        kwargs['GOOGLE_DEVELOPER_MAP_KEY'] = settings.GOOGLE_DEVELOPER_MAP_KEY
        kwargs['beacon_location'] = json.dumps([{"id": "usa000f3e4",
                                                 "name": "device 1",
                                                 "coordinates": [33.487007, -117.143784]},
                                                {"id": "usa000f3e4",
                                                 "name": "device 2",
                                                 "coordinates": [41.653934, -81.450394]},
                                                {"id": "usa000f3e4",
                                                 "name": "device 3",
                                                 "coordinates": [46.602070, -120.505898]},
                                                {"id": "usa000f3e4",
                                                 "name": "device 4",
                                                 "coordinates": [28.018349, -82.764473]},
                                                {"id": "usa000f3e4",
                                                 "name": "device 5",
                                                 "coordinates": [38.018349, -88.764473]}
                                                ])
        return kwargs


class DeleteConfirmModalView(LoginRequiredMixin, TemplateView):
    """Beacons DeleteConfirmModal"""
    template_name = 'ccc/beacons/delete_confirm_modal.html'


class DeviceFormView(LoginRequiredMixin, TemplateView):
    """Get device form"""
    template_name = 'ccc/beacons/devices/device_form.html'


class ContentFormView(LoginRequiredMixin, TemplateView):
    """Get content form"""
    template_name = 'ccc/beacons/contents/content_form.html'
