from django.conf.urls import url
from django.views.generic import TemplateView
from rest_framework.routers import DefaultRouter

from ccc.contacts.api_views import (ContactsForCampaignView, GoogleImportView,
                                    OutlookImportView, YahooAuthorizeView,
                                    YahooGetAuthUrlView)
from ccc.contacts.views_old import (AddContactsToCampaign, AddContactsToGroup,
                                    ContactCampaignsViewSet,
                                    ContactCheckinCreate,
                                    ContactCompanySocialView,
                                    ContactGroupListView, ContactGroupViewSet,
                                    ContactSignupView,
                                    ContactSocialProfileView, ContactViewSet,
                                    CreateContactGroupView, CreateContactView,
                                    DeleteContactGroupView, EditContactView,
                                    ImportSystemUsersView,
                                    PreviewImportContactsView, contacts,
                                    delete_contact, note,
                                    validate_import_contacts)

router = DefaultRouter()
router.register(r'contact', ContactViewSet)
router.register(r'contact-groups', ContactGroupViewSet)
router.register(r'contact-campaigns', ContactCampaignsViewSet)

urlpatterns = [
    url(r'contacts/(?P<contact_id>\d+)/company/(?P<company_id>\d+)/', ContactCompanySocialView.as_view(),
        name="company_profile"),
    url(r'contacts/(?P<contact_id>\d+)/social/(?P<social_id>\d+)/', ContactSocialProfileView.as_view(),
        name="contact_profile"),
    url(r'^add-contact/$', CreateContactView.as_view(), name='create_contact'),
    url(r'^contacts/$', contacts, name='contacts'),
    url(r'^groups/$', ContactGroupListView.as_view(), name='contact_groups'),
    url(r'^groups/add/$', CreateContactGroupView.as_view(), name='create_contact_group'),
    url(r'^groups/(?P<pk>\d+)/delete/$', DeleteContactGroupView.as_view(), name='delete_contact_group'),
    url(r'^edit-contact/(?P<pk>\d+)/$', EditContactView.as_view(), name='edit_contact'),
    url(r'^contact-note/(?P<c_id>\d+)/$', note, name='note'),
    url(r'^preview-import-contacts/$', PreviewImportContactsView.as_view(), name='preview_import_contacts'),
    url(r'^validate-import-contacts/$', validate_import_contacts, name='validate_import_contacts'),
    # url(r'^upload-contact/$', 'apps.contacts.views.import_leads', name='import_contacts'),
    url(r'^delete-contact/(?P<id>\d+)/$', delete_contact, name='delete_contact'),

    url(r'^contacts/checkin/$', ContactCheckinCreate.as_view(), name='checkin_create'),

    url(r'^contacts/(?P<campaign_id>\d+)/$', ContactsForCampaignView.as_view(), name='contacts_for_campaign'),
    url(r'^contacts/import_google/$', GoogleImportView.as_view(), name='google_import'),
    url(r'^outlook_connect$', TemplateView.as_view(
        template_name='ccc/contacts/outlook_authorize.html'), name='outlook_connect'),
    url(r'^outlook_authorize/$', OutlookImportView.as_view(), name='outlook_authorize'),

    url(r'^yahoo_get_auth_url/$', YahooGetAuthUrlView.as_view(), name='yahoo_get_auth_url'),
    url(r'^yahoo_connect$', TemplateView.as_view(
        template_name='ccc/contacts/outlook_authorize.html'), name='yahoo_connect'),
    url(r'^yahoo_authorize/$', YahooAuthorizeView.as_view(), name='yahoo_authorize'),

    url(r'^contacts/signup/(?P<pk>\d+)/$', ContactSignupView.as_view(), name='contact_signup'),

    url(r'^add_contacts_to_campaign/$', AddContactsToCampaign.as_view(), name='add_contacts_to_campaign'),
    url(r'^add_contacts_to_group/$', AddContactsToGroup.as_view(), name='add_contacts_to_group'),

    url(r'^import_system_users/$', ImportSystemUsersView.as_view(), name='import_system_users'),
]

urlpatterns = urlpatterns + router.urls
