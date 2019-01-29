from django.urls import include, path
from django.views.generic import TemplateView

from ccc.contacts.views import BusinessCardView
from ccc.views import Home, SetTimeZoneView, TopSearchView

urlpatterns = [
]

app_name = 'crm'

# New Design

new_templates = [
    path('', Home.as_view(), name='home'),
    path('<str:social_id>/<str:user_name>', BusinessCardView.as_view(), name='business_card'),
    # Social
    path('social/', include('ccc.social_media.social.urls', namespace='social')),
    path('facebook/', include('ccc.social_media.facebook.urls', namespace='facebook')),
    # Marketing
    path('marketing/', include('ccc.marketing.urls', namespace='marketing')),
    path('templates/', include('ccc.template_design.urls', namespace='template_design')),
    path('contacts/', include('ccc.contacts.urls', namespace='contacts')),
    path('teams/', include('ccc.teams.urls', namespace='teams')),
    path('assets/', include('ccc.digital_assets.urls', namespace='digital-assets')),
    path('template/design/', include('ccc.template_design.urls')),
    path('training/', TemplateView.as_view(template_name='crm/training/training-videos.html'), name='training-videos'),
    path('packages/', include('ccc.packages.urls', namespace='packages')),
    path('billings/', include('ccc.billing.urls', namespace='billings')),

    path('beacons/', include('ccc.beacons.urls')),
    path('click-to-call/', include('ccc.click_to_call.urls')),
    path('ocr/', include('ccc.ocr.urls', namespace="ocr")),
    path('user/', include('ccc.users.urls', namespace='users')),
    path('pages/', include('ccc.pages.urls', namespace='pages'))
]

new_apis = [
    path('api/users/', include('ccc.users.api.urls', namespace='api_users')),
    # Social
    path('api/social/', include('ccc.social_media.social.api.urls', namespace='api_social')),
    path('api/facebook/', include('ccc.social_media.facebook.api.urls', namespace='api_facebook')),
    # Marketing
    path('api/marketing/', include('ccc.marketing.api.urls', namespace='api_marketing')),
    # Contacts
    path('api/contacts/', include('ccc.contacts.api.urls', namespace='api_contacts')),
    path('api/set-timezone/', SetTimeZoneView.as_view(), name='set-timezone'),
    path('api/search/', TopSearchView.as_view(), name='top-search')
]

urlpatterns += new_templates + new_apis
