"""
Router / Resources for api: /api/marketing/
"""

from django.urls import include, path, re_path
from rest_framework.routers import SimpleRouter

from ccc.marketing.api.views import (AvailablePhoneNumbersListAPIView,
                                     BuyNumbersViewSet,
                                     CommunicationReportsViewSet,
                                     EngagedPhoneNumberListView,
                                     GetPhoneNumberFromTwilioViewSet,
                                     PurchasedPhoneNumberListView,
                                     RedirectNumberViewSet, ReleaseNumberView,
                                     TeamMemberViewSet, TeamViewSet,
                                     UnRedirectedNumbers)

router = SimpleRouter()

app_name = 'api_marketing'

router.register(r'teams', TeamViewSet, base_name='teams')
router.register(r'team_member', TeamMemberViewSet, base_name='teams_member'),
router.register(r'numbers/redirects', RedirectNumberViewSet, base_name='redirect-numbers')
# Exclusively for marketing APIS.
# Please have all modules and submodules decoupled and in a correct API design.
urlpatterns = [
                  re_path(r'^autodialer/', include('ccc.marketing.autodialer.api.urls', namespace='autodialer')),
                  re_path(r'^buy_phone_numbers/$', BuyNumbersViewSet.as_view(), name='buy-phone-numbers'),
                  path('release-phone-number/<int:pk>/', ReleaseNumberView.as_view(), name='release-phone-number'),
                  re_path(r'^check_phone_numbers/$', GetPhoneNumberFromTwilioViewSet.as_view(),
                          name='check-phone-numbers'),
                  re_path(r'^available-phone-numbers/$', AvailablePhoneNumbersListAPIView.as_view(),
                          name='phone-numbers'),
                  re_path(r'^emailtemplates/', include('ccc.marketing.emailtemplates.api.urls',
                                                       namespace='email_template')),
                  re_path(r'^numbers/unredirected/$', UnRedirectedNumbers.as_view(), name='unredirected_numbers'),
                  re_path(r'^', include('ccc.marketing.campaigns.api.urls', namespace='campaigns')),
                  re_path(r'^surveys/', include('ccc.marketing.surveys.api.urls', namespace='surveys')),
                  re_path(r'^engaged-phone-numbers/', EngagedPhoneNumberListView.as_view(),
                          name='engaged-phone-numbers'),
                  re_path(r'^purchased-phone-numbers/', PurchasedPhoneNumberListView.as_view(),
                          name='purchased-phone-numbers'),
                  re_path('communication_report/', CommunicationReportsViewSet.as_view(), name='communication_report'),
              ] + router.urls
