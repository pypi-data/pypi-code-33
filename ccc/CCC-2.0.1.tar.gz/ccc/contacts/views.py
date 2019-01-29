import json

import requests
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView

from ccc.contacts.api.serializers import ContactSerializer
from ccc.contacts.models import Contact
from ccc.mixin import AuthMixin
from ccc.packages.decorators import check_user_subscription

UserProfile = get_user_model()


class BusinessCardView(TemplateView):
    template_name = 'crm/contacts/business_card.html'

    def get_context_data(self, **kwargs):
        context = super(BusinessCardView, self).get_context_data(**kwargs)
        contact = get_object_or_404(Contact, social_id=kwargs.get('social_id'))
        data = ContactSerializer(instance=contact).data
        google_key = settings.GOOGLE_DEVELOPER_MAP_KEY
        context['contact'] = ContactSerializer(instance=contact).data
        context['GOOGLE_DEVELOPER_MAP_KEY'] = google_key
        try:
            address = ''
            for key in ['street', 'city', 'state', 'country', 'zip']:
                address = address + data[key] + ' '
            url = 'https://maps.googleapis.com/maps/api/place/textsearch/json?query={}&key={}'.format(address, google_key)
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                location = data['results'][0]['geometry']['location']
                context['lat'] = location.get('lat')
                context['lng'] = location.get('lng')
        except Exception as ex:
            print(ex)
        return context


class ContactsList(AuthMixin, LoginRequiredMixin, TemplateView):
    template_name = 'crm/contacts/list-view.html'

    @method_decorator(check_user_subscription)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(ContactsList, self).get_context_data(**kwargs)
        context['contacts'] = True
        context['nav_title'] = 'Contacts'
        context['total_users'] = UserProfile.objects.count()
        return context


class ContactsGroupsList(AuthMixin, LoginRequiredMixin, TemplateView):
    template_name = 'crm/contacts/groups.html'

    @method_decorator(check_user_subscription)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(ContactsGroupsList, self).get_context_data(**kwargs)
        context['contacts'] = True
        context['nav_title'] = 'Contact Groups'
        return context
