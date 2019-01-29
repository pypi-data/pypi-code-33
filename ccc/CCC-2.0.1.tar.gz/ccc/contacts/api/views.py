import xlwt
from accounts.models import Account
from django.db import transaction
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from ccc.contacts.api.serializers import (CompanySocialProfileFilter,
                                          CompanySocialProfileSerializer,
                                          ContactFilter, ContactGroupFilter,
                                          ContactGroupSerializer,
                                          ContactNoteSerializer,
                                          ContactSerializer,
                                          ContactSocialProfileFilter,
                                          ContactSocialProfileSerializer,
                                          ImportContactSerializer,
                                          UploadContactSerializer,
                                          ValidateContactUploadSerializer)
from ccc.contacts.models import (CompanySocialProfile, Contact, ContactGroup,
                                 ContactNote, ContactSocialProfile)
from ccc.contacts.serializers import ContactListSerializer
from ccc.mixin import AuthParsersMixin
from ccc.users.models import UserProfile
from ccc.utils.utils import XLSJobImporter


class CreateBusinessCard(AuthParsersMixin, APIView):

    def get(self, request, *args, **kwargs):
        primary_data_point = ['first_name', 'last_name', 'email', 'phone', 'profile_image', 'contact_type']
        contact = Contact.objects.filter(email=request.user.email).first()
        user_data = Account.objects.get(id=request.user.id).__dict__
        data = {'user_id': request.user.id, 'contact_type': 'DBC'}
        for field in primary_data_point:
            try:
                data[field] = user_data[field]
            except KeyError:
                pass
        if contact:
            for field in primary_data_point:
                setattr(contact, field, data[field])
            contact.save()
        else:
            contact = Contact.objects.create(**data)
        return JsonResponse({'status': 'success', 'contact_id': contact.id})


class ContactsViewSet(AuthParsersMixin, ModelViewSet):
    """ Contact View set
        LEAD_TYPE = (
            ('1', "SMS"),
            ('2', "MMS"),
            ('3', "VOICE"),
            ('4', "CSV UPLOAD"),
            ('5', "Card Scan"),
            ('6', "Manual"),
            ('7', "Survey"),
            ('8', "System user import"))
            To filter by group, add URL param '?group=<group_id>'
            You can filter by fields phone, first_name, last_name, email, company_name, start_date, end_date, campaign
            NOTE:
                start_date: start_date < created_date
                end_date: end_date > created_date
                To filter by range add start_date and end_date
    """
    serializer_class = ContactSerializer
    social_serializer_class = ContactSocialProfileSerializer
    serializer_excel_class = ContactListSerializer
    # queryset = Contact.objects.all().order_by('first_name')
    filter_class = ContactFilter
    filter_backends = (SearchFilter, DjangoFilterBackend,)
    search_fields = ('first_name', 'last_name', 'phone', 'note', 'company_name', 'designation', 'email',
                     'campaigns__name')

    def get_queryset(self):
        if self.request.GET.get('group', None):
            return get_object_or_404(ContactGroup, pk=self.request.GET.get('group')) \
                .contacts.filter(user=self.request.user).order_by('first_name')
        return Contact.objects.filter(user=self.request.user).order_by('first_name')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @transaction.non_atomic_requests
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        social = {}
        social_fields = [f.name for f in ContactSocialProfile._meta.get_fields()]
        for field in social_fields:
            if request.data.get(field):
                social[field] = request.data[field]
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        if social:
            self.serializer_class = self.social_serializer_class
            serializer = self.get_serializer(instance.social_profiles.first(), data=social, partial=partial)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}
        return JsonResponse({'Success': 'Save contact details'})

    @action(methods=['get'], detail=False)
    def export_contact(self, request, *args, **kwargs):
        object_list = self.queryset.filter(user=request.user)
        return self.generate_contact_excel(object_list)

    def generate_contact_excel(self, object_list):
        self.serializer_class = self.serializer_excel_class
        object_list = self.get_serializer(object_list, many=True)
        s1 = xlwt.Workbook(encoding="utf-8")
        # sheets = s1.set_active_sheet(0)
        # sheets = s1.get_sheet(0)
        sheets = s1.add_sheet("Contact list", cell_overwrite_ok=True)
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

    @action(methods=['post'], detail=False)
    def import_system_user(self, request, *args, **kwargs):
        self.serializer_class = ImportContactSerializer
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        campaigns = data.get('campaigns')
        groups = data.get('groups')
        contacts = []

        for user in UserProfile.objects.exclude(pk=request.user.pk).exclude(email='', phone=None):
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
        if contacts:
            for contact in contacts:
                if campaigns:
                    for campaign in campaigns:
                        contact.campaigns.add(campaign)
                if groups:
                    for group in groups:
                        group.contacts.add(contact)
            return JsonResponse({'message': 'System user imported'}, status=201)
        return JsonResponse({'message': 'Not found contact'}, status=404)

    @action(methods=['post'], detail=False)
    def excel_preview(self, request, *args, **kwargs):
        self.serializer_class = UploadContactSerializer
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        excel = data.get('excel')
        importer = XLSJobImporter(excel.read())
        rows = importer.preview()
        col_header = ((None, '---'),
                      ('first_name', 'First name', True),
                      ('last_name', 'Last name', True),
                      ('email', 'Email', True),
                      ('phone', 'Phone', True),
                      ('company_name', 'Company name', True),
                      ('custom', 'Custom'))

        return JsonResponse({
            'rows': rows,
            'col_heads': col_header,
            'num_cols': len(rows) and list(range(len(rows[0]))) or [],
            'campaigns': data.get('campaigns'),
            'groups': data.get('groups')
        })

    @action(methods=['post'], detail=False)
    def import_from_file(self, request, *args, **kwargs):
        default_selection = {"col_type_0": "first_name",
                             "col_type_1": "last_name",
                             "col_type_2": "email",
                             "col_type_3": "phone",
                             "col_type_4": "company_name"}
        self.serializer_class = ValidateContactUploadSerializer
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        excel = data.get('excel')
        drop_first_row = data.get('drop_first_row')
        campaigns = data.get('campaigns', [])
        groups = data.get('groups', [])
        excel_content = excel.read()
        importer = XLSJobImporter(excel_content)

        num_of_cols = len([x for x in default_selection.keys() if x.startswith('col_type_')])
        col_types = []
        for n in range(num_of_cols):
            col_key = 'col_type_%d' % n
            if not default_selection.get(col_key) or default_selection[col_key] in ['', "None"]:
                col_types.append(default_selection.get(col_key))
            else:
                col_types.append(default_selection.get(col_key))
        col_custom_names = [data.get('col_custom_name_%d' % n) for n in range(num_of_cols)]
        invalid_rows = importer.validate_all(
            col_types, col_custom_names, drop_first_row)

        if invalid_rows:
            col_headers = ['']
            for i in range(len(col_types)):
                if col_types[i] == 'custom':
                    col_headers.append(col_custom_names[i])
                else:
                    col_headers.append(col_types[i])

            return JsonResponse({
                'invalid_rows': invalid_rows,
                'num_cols': len(invalid_rows) and list(range(len(invalid_rows[0]))) or [],
                'col_headers': col_headers
            }, status=status.HTTP_400_BAD_REQUEST)
        else:
            importer.import_all(request.user, col_types, col_custom_names, drop_first_row, campaigns=campaigns,
                                groups=groups)
            return JsonResponse({'num_of_records': "Importing contacts in asynchronous way"},
                                status=status.HTTP_201_CREATED)

    @action(['GET'], url_path='ids', detail=False)
    def contact_ids(self, request):
        queryset = self.get_queryset()
        queryset = self.filter_queryset(queryset)
        queryset = queryset.values_list('id', flat=True)
        return Response(list(queryset), status=status.HTTP_200_OK)


class ContactGroupViewSet(AuthParsersMixin, ModelViewSet):
    """Contact Group viewset """
    serializer_class = ContactGroupSerializer
    queryset = ContactGroup.objects.all().order_by('name')
    filter_class = ContactGroupFilter

    def get_queryset(self):
        return ContactGroup.objects.filter(user=self.request.user).order_by('-created_at')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class CompanySocialProfileViewSet(AuthParsersMixin, ModelViewSet):
    """Company social profile view"""
    serializer_class = CompanySocialProfileSerializer
    queryset = CompanySocialProfile.objects.all()
    filter_class = CompanySocialProfileFilter


class ContactSocialProfileViewSet(AuthParsersMixin, ModelViewSet):
    """Company social profile view"""
    serializer_class = ContactSocialProfileSerializer
    queryset = ContactSocialProfile.objects.all()
    filter_class = ContactSocialProfileFilter


class ContactNotesViewSet(AuthParsersMixin, ModelViewSet):
    serializer_class = ContactNoteSerializer
    pagination_class = None

    def get_queryset(self):
        contact_id = self.request.query_params.get('contact_id')
        contact_phone = self.request.query_params.get('contact_phone')
        queryset = ContactNote.objects.filter(contact__user=self.request.user).order_by('-created_at')
        if contact_id:
            queryset = queryset.filter(contact_id=contact_id)
        if contact_phone:
            phone = '+' + contact_phone.lstrip()
            queryset = queryset.filter(contact__phone=phone)
        return queryset

    def perform_create(self, serializer):
        contact_phone = self.request.query_params.get('contact_phone')
        if contact_phone:
            phone = '+' + contact_phone.lstrip()
            contact = Contact.objects.filter(phone=phone)
            if contact.exists():
                contact = contact.first()
            else:
                contact = Contact.objects.create(lead_type='3', phone=phone, user=self.request.user)
            serializer.save(contact=contact)
        else:
            serializer.save()
