import json
import os
from logging import getLogger

from annoying.functions import get_object_or_None
from dateutil import parser
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Count, Q
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.templatetags.static import static
from django.urls import reverse, reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import ListView, TemplateView
from django.views.generic.edit import (CreateView, DeleteView, FormView,
                                       UpdateView)
from rest_framework import status, viewsets
from rest_framework.response import Response
from waffle.decorators import waffle_flag

from ccc.campaigns.models import OSMS, Campaign
from ccc.campaigns.serializers import CampaignNameSerializer
from ccc.common.mixins import (AjaxableResponseMixin, AjaxDeletionMixin,
                               LoginRequiredAjaxMixin, LoginRequiredMixin,
                               OnlyOwnerObjectRequiredMixin,
                               StaffRequiredMixin)
from ccc.contacts.cloud_tasks import trigger_contact_import
from ccc.contacts.lead_importer import XLSJobImporter
from ccc.contacts.models import (CompanySocialProfile, Contact, ContactCheckin,
                                 ContactGroup, ContactNote, ContactProperty,
                                 ContactSocialProfile)
from ccc.contacts.serializers import (ContactGroupListSerializer,
                                      ContactListSerializer,
                                      LimitedContactListSerializer)
from ccc.contacts.utils import StandardResultsSetPagination
from ccc.ocr.models import ImageContacts
from ccc.survey.models import Survey
from ccc.survey.views import TwilioSMSHandler
from ccc.users.models import UserProfile

from .forms import (AddContactsToCampaignForm, AddContactsToGroupForm,
                    ContactCheckinForm, ContactSignupForm,
                    CreateContactGroupForm, CreateEditContactForm,
                    ImportContactForm, UploadContactForm)

log = getLogger(__name__)

ACCOUNT_SID = settings.TWILIO_SID
AUTH_TOKEN = settings.TWILIO_TOKEN


@login_required
def contacts(request):
    campaigns = Campaign.objects.filter(user=request.user, active=True) \
        .extra(select={'lower_name': 'lower(name)'}) \
        .order_by('lower_name')

    groups = ContactGroup.objects.filter(user=request.user) \
        .extra(select={'lower_name': 'lower(name)'}) \
        .order_by('lower_name')

    surveys = Survey.objects.filter(user=request.user, active=True) \
        .extra(select={'lower_name': 'lower(title)'}) \
        .order_by('lower_name')

    contact_checkin_form = ContactCheckinForm()
    contact_checkin_form.fields["campaign"].queryset = campaigns

    add_contact_form = CreateEditContactForm(user=request.user)
    upload_contact_form = UploadContactForm(user=request.user)
    import_contact_form = ImportContactForm(user=request.user)
    import_users_form = ImportContactForm(user=request.user)

    users = UserProfile.objects.exclude(
        pk=request.user.pk).exclude(email='', phone=None).distinct()

    microsoft_redirect_uri = request.build_absolute_uri(
        reverse('outlook_connect'))

    return render(request, 'ccc/contacts/contacts.html', {
        'campaigns': campaigns,
        'groups': groups,
        'surveys': surveys,
        'contact_checkin_form': contact_checkin_form,
        'add_contact_form': add_contact_form,
        'upload_contact_form': upload_contact_form,
        'import_contact_form': import_contact_form,
        'import_users_form': import_users_form,
        'all_users': users.count(),
        'microsoft_client_id': settings.MICROSOFT_CLIENT_ID,
        'microsoft_redirect_uri': microsoft_redirect_uri,
    })


class ContactGroupListView(LoginRequiredMixin, ListView):
    template_name = 'ccc/contacts/contactgroup_list.html'

    def get_queryset(self):
        return ContactGroup.objects.filter(user=self.request.user).annotate(num_contacts=Count('contacts'))

    def get_context_data(self, **kwargs):
        ctx = super(ContactGroupListView, self).get_context_data(**kwargs)
        ctx['create_contact_form'] = CreateContactGroupForm()
        return ctx


class CreateContactGroupView(LoginRequiredAjaxMixin, AjaxableResponseMixin, CreateView):
    model = ContactGroup
    form_class = CreateContactGroupForm

    def get_form_kwargs(self):
        kwargs = super(CreateContactGroupView, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        self.object = form.save()
        return self.render_to_json_response({
            'status': 'success',
            'redirect_to': reverse('contact_groups')
        })


class DeleteContactGroupView(LoginRequiredMixin, AjaxDeletionMixin, OnlyOwnerObjectRequiredMixin, DeleteView):
    model = ContactGroup
    success_url = reverse_lazy('contact_groups')


class CreateContactView(SuccessMessageMixin, LoginRequiredMixin, CreateView):
    model = Contact
    form_class = CreateEditContactForm
    success_message = 'Contact created'

    def get_form_kwargs(self):
        kwargs = super(CreateContactView, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        contact = form.save(commit=False)
        contact.user = self.request.user
        contact.lead_type = 6
        contact.save()

        campaigns = form.cleaned_data.get('campaigns')
        for campaign in campaigns:
            contact.campaigns.add(campaign)

        groups = form.cleaned_data.get('groups')
        for group in groups:
            group.contacts.add(contact)

        return HttpResponse(json.dumps({
            "message": self.success_message
        }))

    def form_invalid(self, form):
        return HttpResponse(
            json.dumps(form.errors),
            status=400,
            content_type="application/json")

    def get_success_url(self):
        return reverse('contacts')


class EditContactView(SuccessMessageMixin, LoginRequiredMixin, UpdateView):
    model = Contact
    form_class = CreateEditContactForm
    success_message = 'Contact changed'
    template_name = 'ccc/contacts/edit_contact_modal.html'

    def get_initial(self):
        initial = super(EditContactView, self).get_initial()
        initial['campaigns'] = self.object.campaigns.all()
        initial['groups'] = self.object.groups.all()
        return initial

    def get_form_kwargs(self):
        kwargs = super(EditContactView, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        # Save self.object first
        form.save()

        # Handle campaign changes (add/remove)
        initial_campaign_set = set(self.object.campaigns.all())
        changed_campaign_set = set(form.cleaned_data.get('campaigns'))

        campaigns_to_remove = initial_campaign_set - changed_campaign_set
        campaigns_to_add = changed_campaign_set - initial_campaign_set

        for campaign in campaigns_to_add:
            self.object.campaigns.add(campaign)

        for campaign in campaigns_to_remove:
            self.object.campaigns.remove(campaign)

        # Handle group changes (add/remove)
        initial_group_set = set(self.object.groups.all())
        changed_group_set = set(form.cleaned_data.get('groups'))

        groups_to_remove = initial_group_set - changed_group_set
        groups_to_add = changed_group_set - initial_group_set

        for group in groups_to_add:
            group.contacts.add(self.object)

        for group in groups_to_remove:
            group.contacts.remove(self.object)

        # Return response
        return HttpResponse(json.dumps({
            "message": self.success_message
        }))

    def form_invalid(self, form):
        return HttpResponse(
            json.dumps(form.errors),
            status=400,
            content_type="application/json")


@login_required
def delete_contact(request, id):
    contact = get_object_or_404(Contact, pk=id,
                                user=request.user)
    contact.delete()

    messages.info(
        request,
        'Contact "%s" has been deleted successfully.' % (
            contact.first_name or "No Name")
    )
    return HttpResponseRedirect(reverse('contacts'))


def note(request, c_id=0):
    if request.method == 'GET':
        notes = ContactNote.objects.filter(
            contact=c_id).order_by('-created_at')

        return render(request, 'ccc/contacts/contact_note.html', locals())

    elif request.method == 'POST':
        note = request.POST.get('note', '')

        if note == '':
            pass
        else:
            c = get_object_or_None(Contact, id=c_id)
            ContactNote.objects.create(note=note, contact=c)

        return HttpResponseRedirect('/contacts/')


def handle_uploaded_file(f):
    filename, extension = os.path.splitext(f.name)
    full_path = "media/campaigns/email/templates/%s" % f.name
    with open(full_path, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)
    return full_path


class PreviewImportContactsView(LoginRequiredAjaxMixin, AjaxableResponseMixin, FormView):
    form_class = UploadContactForm

    def get_form_kwargs(self):
        kwargs = super(PreviewImportContactsView, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_invalid(self, form):
        return self.render_to_json_response(form.errors, status=400)

    def form_valid(self, form):
        excel = form.cleaned_data.get('excel')
        excel_file_path = handle_uploaded_file(excel)
        importer = XLSJobImporter(open(excel_file_path))
        rows = importer.preview()
        col_header = ((None, '---'),
                      ('first_name', 'First name', True),
                      ('last_name', 'Last name', True),
                      ('email', 'Email', True),
                      ('phone', 'Phone', True),
                      ('company_name', 'Company name', True),
                      ('custom', 'Custom'))
        return render(self.request, 'modals/import_preview.html', {
            'rows': rows,
            'col_heads': col_header,
            'num_cols': len(rows) and range(len(rows[0])) or [],
            'excel_file_path': excel_file_path,
            'campaigns': form.cleaned_data.get('campaigns'),
            'groups': form.cleaned_data.get('groups'),
            'form': form,
        })


@csrf_exempt
def validate_import_contacts(request):
    # TODO: class based view; form validation
    default_selection = {"col_type_0": "first_name",
                         "col_type_1": "last_name",
                         "col_type_2": "email",
                         "col_type_3": "phone",
                         "col_type_4": "company_name"}

    drop_first_row = request.POST.get('drop_first_row', None)

    excel_file_path = request.POST.get('excel_file_path', None)

    campaigns = Campaign.objects.filter(
        pk__in=request.POST.getlist('campaigns', []), user=request.user)
    groups = ContactGroup.objects.filter(
        pk__in=request.POST.getlist('groups', []), user=request.user)

    importer = XLSJobImporter(open(excel_file_path))

    num_of_cols = len(
        filter(lambda x: x.startswith('col_type_'), request.POST.keys()))
    col_types = []
    for n in range(num_of_cols):
        col_key = 'col_type_%d' % n
        if not request.POST.get(col_key) or request.POST[col_key] in ['', "None"]:
            col_types.append(default_selection.get(col_key))
        else:
            col_types.append(request.POST.get(col_key))

    col_custom_names = [
        request.POST.get('col_custom_name_%d' % n) for n in range(num_of_cols)]
    invalid_rows = importer.validate_all(
        col_types, col_custom_names, drop_first_row)

    if invalid_rows:
        col_headers = ['']
        for i in range(len(col_types)):
            if col_types[i] == 'custom':
                col_headers.append(col_custom_names[i])
            else:
                col_headers.append(col_types[i])

        return render(request, 'modals/import_errors.html', {
            'invalid_rows': invalid_rows,
            'num_cols': len(invalid_rows) and range(len(invalid_rows[0])) or [],
            'col_headers': col_headers
        })
    else:
        # no ivalid rows, import them!

        # TODO: store extra columns?
        # custom_properties = [c for c in col_custom_names if c]
        # for property_name in custom_properties:
        #   ...

        # Async task
        trigger_contact_import(
            excel_file_path=excel_file_path,
            user=request.user,
            col_types=col_types,
            col_custom_names=col_custom_names,
            drop_first_row=drop_first_row,
            campaigns=campaigns, groups=groups).execute()

        return render(request, 'modals/import_successful.html',
                      {'num_of_records': "Importing contacts in asynchronous way"})


class ContactCheckinCreate(SuccessMessageMixin, LoginRequiredMixin,
                           CreateView):
    model = ContactCheckin
    success_message = "%(contact)s Checkin successful"
    form_class = ContactCheckinForm

    @method_decorator(waffle_flag('Contact Checkin'))
    def dispatch(self, *args, **kwargs):
        return super(ContactCheckinCreate, self).dispatch(*args, **kwargs)

    def get_form(self, form_class=None):
        form = super(ContactCheckinCreate, self).get_form(form_class)
        form.fields['campaign'].queryset = Campaign.objects.filter(
            user=self.request.user,
            active=True).order_by('-id')
        form.fields['contact'].queryset = Contact.objects.filter(
            user=self.request.user)
        return form

    def form_invalid(self, form):
        return HttpResponse(
            json.dumps(form.errors),
            status=400,
            content_type="application/json")

    def form_valid(self, form):
        super(ContactCheckinCreate, self).form_valid(form)
        if form.instance.contact.phone and form.instance.sms and \
            self.request.user.balance.get('sms', 0) > 0:
            OSMS.objects.create(
                from_no=form.instance.campaign.phone.twilio_number,
                campaign=form.instance.campaign,
                to=form.instance.contact.phone,
                text=form.instance.sms,
                countdown=form.instance.delay)

        return HttpResponse(json.dumps({
            "message": self.success_message
        }))

    def get_success_url(self):
        return reverse('contacts')


class ContactSignupView(CreateView):
    model = Contact
    template_name = 'ccc/contacts/ccc_embed_form.html'
    form_class = ContactSignupForm

    @csrf_exempt
    def dispatch(self, *args, **kwargs):
        self.campaign = get_object_or_404(Campaign, pk=kwargs.get('pk'))
        return super(ContactSignupView, self).dispatch(*args, **kwargs)

    def get_form_kwargs(self):
        form_kwargs = super(ContactSignupView, self).get_form_kwargs()
        form_kwargs['campaign'] = self.campaign
        return form_kwargs

    def get_context_data(self, **kwargs):
        ctx = super(ContactSignupView, self).get_context_data(**kwargs)
        ctx['style_absolute_uri'] = self.request.build_absolute_uri(
            static('assets/css/ccc_embed_form_style.css'))
        ctx['script_absolute_uri'] = self.request.build_absolute_uri(
            static('assets/scripts/ccc_embed_form_scripts.js'))
        ctx['action_absolute_uri'] = self.request.build_absolute_uri(
            reverse('contact_signup', args=[self.campaign.pk]))
        ctx['campaign'] = self.campaign
        return ctx

    def form_invalid(self, form):
        return render(self.request, 'ccc/contacts/ccc_embed_form_inner.html',
                      self.get_context_data(form=form))

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.user = self.campaign.user
        self.object.save()
        self.object.campaigns.add(self.campaign)

        for extra_field in self.campaign.signup_extra_fields.all():
            property_value = form.cleaned_data.get(
                'property_%s' % extra_field.pk, None)
            if property_value:
                cp, created = ContactProperty.objects.get_or_create(
                    contact=self.object, name=extra_field.name)
                cp.value = property_value
                cp.save()

        return render(self.request, 'ccc/contacts/ccc_embed_success.html', {
            'success_message': self.campaign.embed_form_success or 'Thank you!'})


class AddContactsToCampaign(LoginRequiredAjaxMixin, AjaxableResponseMixin, FormView):
    form_class = AddContactsToCampaignForm

    def get_form_kwargs(self):
        kwargs = super(AddContactsToCampaign, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_invalid(self, form):
        return self.render_to_json_response(form.errors, status=400)

    def form_valid(self, form):
        contacts = form.cleaned_data.get('contacts')
        campaign = form.cleaned_data.get('campaign_to_add')

        for contact in contacts:
            contact.campaigns.add(campaign)

        return self.render_to_json_response({
            'status': 'success',
            'redirect_to': reverse('contacts')
        })


class AddContactsToGroup(LoginRequiredAjaxMixin, AjaxableResponseMixin, FormView):
    form_class = AddContactsToGroupForm

    def get_form_kwargs(self):
        kwargs = super(AddContactsToGroup, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_invalid(self, form):
        return self.render_to_json_response(form.errors, status=400)

    def form_valid(self, form):
        contacts = form.cleaned_data.get('contacts')
        group = form.cleaned_data.get('group_to_add')

        for contact in contacts:
            group.contacts.add(contact)

        return self.render_to_json_response({
            'status': 'success',
            'redirect_to': reverse('contacts')
        })


class ImportSystemUsersView(LoginRequiredMixin, StaffRequiredMixin, FormView):
    form_class = ImportContactForm

    def get_form_kwargs(self):
        kwargs = super(ImportSystemUsersView, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        campaigns = form.cleaned_data.get('campaigns')
        groups = form.cleaned_data.get('groups')
        contacts = []

        for user in UserProfile.objects.exclude(pk=self.request.user.pk).exclude(email='', phone=None):
            # for user in UserProfile.objects.exclude(pk=self.request.user.pk):
            if user.phone:
                contact = Contact.objects.filter(user=self.request.user,
                                                 phone=user.phone).first()
            elif user.email:
                contact = Contact.objects.filter(user=self.request.user,
                                                 email=user.email).first()
            else:
                continue

            if contact:
                updated = False
                # update email, phone, first_name, last_name if necessary
                for attr in ('email', 'phone', 'first_name', 'last_name'):
                    if not getattr(contact, attr, False):
                        setattr(contact, attr, getattr(user, attr, None))
                        updated = True
                if updated:
                    contact.save()
            else:
                contact = Contact.objects.create(
                    first_name=user.first_name,
                    last_name=user.last_name,
                    email=user.email,
                    phone=user.phone,
                    user=self.request.user,
                    lead_type=8)

            contacts.append(contact)

        for contact in contacts:
            for campaign in campaigns:
                contact.campaigns.add(campaign)

            for group in groups:
                group.contacts.add(contact)

        return HttpResponseRedirect(reverse('contacts'))


class ContactViewSet(viewsets.ModelViewSet):
    """
        Class for handling Movie request
    """
    serializer_class = ContactListSerializer
    model = Contact
    queryset = Contact.objects.all()
    paginate_by = 10
    pagination_class = StandardResultsSetPagination

    def generate_contact_excel(self, object_list):
        import xlwt
        object_list = self.get_serializer(object_list, many=True)
        s1 = xlwt.Workbook(encoding="utf-8")
        # sheets = s1.set_active_sheet(0)
        # sheets = s1.get_sheet(0)
        sheets = s1.add_sheet("Survey Response", cell_overwrite_ok=True)
        first = ['Date created', 'Name', 'Phone', 'Email', 'campaigns', 'Groups', 'Survey']

        sheets.col(first.index('Date created')).width = 256 * 20
        sheets.col(first.index('Name')).width = 256 * 30
        sheets.col(first.index('Phone')).width = 256 * 15
        sheets.col(first.index('Email')).width = 256 * 40
        sheets.col(first.index('campaigns')).width = 256 * 30
        sheets.col(first.index('Groups')).width = 256 * 20
        sheets.col(first.index('Survey')).width = 256 * 30

        self.grey_style = xlwt.XFStyle()
        self.grey_style.font.bold = True
        self.grey_style.font.colour_index = xlwt.Style.colour_map[
            'white']
        pattern = xlwt.Pattern()
        pattern.pattern = xlwt.Pattern.SOLID_PATTERN
        pattern.pattern_background_colour = xlwt.Style.colour_map['gray50']
        self.grey_style.pattern = pattern
        self.grey_style.alignment.horz = xlwt.Alignment.HORZ_CENTER_ACROSS_SEL

        style = xlwt.XFStyle()
        style.font.bold = True
        pattern = xlwt.Pattern()
        pattern.pattern = xlwt.Pattern.SOLID_PATTERN
        pattern.pattern_background_colour = xlwt.Style.colour_map['gray50']
        style.pattern = pattern
        style.alignment.horz = xlwt.Alignment.HORZ_CENTER_ACROSS_SEL
        sheets.write_merge(0, 0, 0, len(first), "Contact List", style=self.grey_style)
        for i, x in enumerate(first):
            sheets.write(2, i, x, style)

        starting_posotion = 3
        for obj in object_list.data:
            custom_height = min(max(len(obj["campaigns_names"]), len(obj["groups_names"]), 1), 5)
            sheets.row(starting_posotion).height_mismatch = True
            sheets.row(starting_posotion).height = 256 * custom_height

            sheets.write(starting_posotion, first.index('Date created'), obj["created_at"] or '')
            sheets.write(starting_posotion, first.index('Name'), u"{} {}".format(
                obj["first_name"] or '', obj["last_name"] or ''))
            sheets.write(starting_posotion, first.index('Phone'), obj["phone"] or '')
            sheets.write(starting_posotion, first.index('Email'), obj["email"] or '')
            sheets.write(starting_posotion, first.index('campaigns'), "\n".join(obj["campaigns_names"]) or '')
            sheets.write(starting_posotion, first.index('Groups'), "\n".join(obj["groups_names"]) or '')
            sheets.write(starting_posotion, first.index('Survey'), "\n".join(obj["surveys_names"]) or '')
            starting_posotion += 1

        response = HttpResponse(content_type="application/ms-excel")
        response[
            'Content-Disposition'] = 'attachment; filename="{}.xls"'.format("contact_list")
        s1.save(response)
        return response

    def create(self, request, *args, **kwargs):
        log.info("contacts request data = {}".format(request.data))
        if request.data.get("phone"):
            try:
                request.data._mutable = True
                request.data["phone"] = str(request.data["phone"]).replace("-", "").strip()
                request.data._mutable = False
            except Exception:
                request.data["phone"] = str(request.data["phone"]).replace("-", "").strip()

        campaign_obj = None
        survey_obj = None
        queryset = None
        if request.data.get("campaign_id") and request.data.get("survey_id"):
            data = {"Message": "campaign_id and survey_id both are present"}
            return Response(data, status=status.HTTP_400_BAD_REQUEST)

        if request.data.get("campaign_id"):
            campaign_filter = Campaign.objects.filter(id=request.data["campaign_id"],
                                                      user=request.user)
            if campaign_filter.exists():
                campaign_obj = campaign_filter[0]
            else:
                data = {"Message": "Campaign Object not found"}
                return Response(data, status=status.HTTP_400_BAD_REQUEST)

        if request.data.get("survey_id"):
            survey_filter = Survey.objects.filter(id=request.data["survey_id"],
                                                  user=request.user)
            if survey_filter.exists():
                survey_obj = survey_filter[0]
            else:
                data = {"Message": "Survey Object not found"}
                return Response(data, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            serializer.instance.lead_type = 5
            serializer.instance.user = request.user
            if campaign_obj:
                serializer.instance.campaigns.add(campaign_obj)
            if survey_obj and serializer.instance.phone and survey_obj.phone:
                serializer.instance.survey = survey_obj
                serializer.instance.save()
                to = survey_obj.phone.twilio_number
                from_ = serializer.instance.phone
                TwilioSMSHandler.trigger_survey(from_=from_, to=to, body="Trigger Survey", manual_trigger=True,
                                                lead_type=5)

            if request.data.get("uuid"):
                uuid_data = request.data["uuid"]
                ImageContacts.objects.filter(unique_upload_id=uuid_data).update(is_processed=True)
                serializer.instance.card_image_uuid = uuid_data
            serializer.instance.save()
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def list(self, request, *args, **kwargs):
        try:
            self.object_list = Contact.objects.filter(user=request.user)
            campaign_id = request.query_params.get('campaign_id')
            group_id = request.query_params.get('group_id')
            survey_id = request.query_params.get('survey_id')
            if campaign_id not in [None, '', 'undefined']:
                if str(campaign_id) == "0":
                    self.object_list = self.object_list.filter(
                        campaigns__isnull=True)
                else:
                    campaigns_ids = Campaign.objects.filter(id=campaign_id)
                    self.object_list = self.object_list.filter(
                        campaigns__id__in=campaigns_ids)

            if survey_id not in [None, '', 'undefined']:
                if str(survey_id) == "0":
                    self.object_list = self.object_list.filter(
                        survey__isnull=True)
                else:
                    self.object_list = self.object_list.filter(
                        survey__id=survey_id)

            if group_id not in [None, '', 'undefined']:
                if str(group_id) == "0":
                    self.object_list = self.object_list.filter(
                        groups__isnull=True)
                else:
                    groups_ids = ContactGroup.objects.filter(id=group_id)
                    self.object_list = self.object_list.filter(
                        groups__id__in=groups_ids)
            if request.query_params.get("only_phone"):
                self.object_list = self.object_list.exclude(
                    phone__isnull=True).exclude(phone__exact='')
            if request.query_params.get("search") not in [None, '', 'undefined']:
                text_search = request.query_params["search"]
                text_list = str(text_search).strip().split(" ")
                query = Q()
                for text in text_list:
                    query |= Q(first_name__icontains=text)
                    query |= Q(last_name__icontains=text)
                    query |= Q(email__icontains=text)
                    query |= Q(phone__icontains=text)
                self.object_list = self.object_list.filter(query)

            if request.query_params.get("filter_start_date"):
                dt = parser.parse(request.query_params["filter_start_date"].split("GMT")[0].strip())
                dt = dt.replace(hour=0, minute=0, second=0)
                self.object_list = self.object_list.filter(created_at__gte=dt)

            if request.query_params.get("filter_end_date"):
                dt = parser.parse(request.query_params["filter_end_date"].split("GMT")[0].strip())
                dt = dt.replace(hour=23, minute=59, second=59)
                self.object_list = self.object_list.filter(created_at__lte=dt)

            self.object_list = self.object_list.order_by('-created_at')
            if request.query_params.get("export_data"):
                return self.generate_contact_excel(self.object_list)
        except Exception as ex:
            log.exception("Exception in Contact API = {}".format(ex))
            self.object_list = []

        if request.query_params.get('limited_fields'):
            self.serializer_class = LimitedContactListSerializer

        page = self.paginate_queryset(self.object_list)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
        else:
            serializer = self.get_serializer(self.object_list, many=True)
        return self.get_paginated_response(serializer.data)


class ContactGroupViewSet(viewsets.ModelViewSet):
    """
        Class for handling Movie request
    """
    serializer_class = ContactGroupListSerializer
    model = ContactGroup
    queryset = ContactGroup.objects.all()
    paginate_by = 10

    def list(self, request, *args, **kwargs):
        try:
            self.object_list = ContactGroup.objects.filter(user=request.user)
            self.object_list = self.object_list.order_by('name')
        except Exception as ex:
            print("Exception in Contact API", ex)
            self.object_list = []

        page = self.paginate_queryset(self.object_list)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(self.object_list, many=True)
        return Response(serializer.data)


class ContactCampaignsViewSet(viewsets.ModelViewSet):
    """
        Class for handling Movie request
    """
    serializer_class = CampaignNameSerializer
    model = Campaign
    queryset = Campaign.objects.all()
    paginate_by = 10

    def list(self, request, *args, **kwargs):
        try:
            self.object_list = Campaign.objects.filter(user=request.user, active=True)
            self.object_list = self.object_list.order_by('name')
        except Exception as ex:
            print("Exception in Contact API", ex)
            self.object_list = []

        page = self.paginate_queryset(self.object_list)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(self.object_list, many=True)
        return Response(serializer.data)


class ContactCompanySocialView(TemplateView):
    """Contact company template view"""
    template_name = 'ccc/contacts/company_social_profile.html'

    def get_context_data(self, **kwargs):
        """set context"""
        context = super(ContactCompanySocialView, self).get_context_data(**kwargs)
        context['company_profile'] = CompanySocialProfile.objects.filter(contact__id=kwargs.get('contact_id')).first()
        return context


class ContactSocialProfileView(TemplateView):
    """Contact company template view"""
    template_name = 'ccc/contacts/contact_social_profile.html'

    def get_context_data(self, **kwargs):
        """set context"""
        context = super(ContactSocialProfileView, self).get_context_data(**kwargs)
        context['contact_profile'] = ContactSocialProfile.objects.filter(contact__id=kwargs.get('contact_id')).first()
        return context
