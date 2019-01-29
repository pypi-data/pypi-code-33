from rest_framework.routers import DefaultRouter
from django.urls import path
from ccc.contacts.api.views import (CompanySocialProfileViewSet,
                                    ContactGroupViewSet, ContactNotesViewSet,
                                    ContactSocialProfileViewSet,
                                    ContactsViewSet, CreateBusinessCard)

app_name = 'contacts'

router = DefaultRouter()
router.register(r'notes', ContactNotesViewSet, base_name='contact-notes')
router.register(r'groups', ContactGroupViewSet, base_name='group')
router.register(r'company_social', CompanySocialProfileViewSet, base_name='company_social')
router.register(r'contact_social', ContactSocialProfileViewSet, base_name='contact_social')
router.register(r'', ContactsViewSet, base_name='contact')

urlpatterns = [
    path('business_card/', CreateBusinessCard.as_view(), name='create_business_card'),
] + router.urls
