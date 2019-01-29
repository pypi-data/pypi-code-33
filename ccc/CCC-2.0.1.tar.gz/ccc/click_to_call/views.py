import json
from collections import OrderedDict, deque
from math import ceil

import xlwt
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.http.response import HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.base import TemplateView, View
from phonenumber_field.phonenumber import to_python
from rest_framework import generics
from twilio.jwt.client import ClientCapabilityToken
from twilio.twiml.voice_response import VoiceResponse

from ccc.campaigns.models import Campaign
from ccc.click_to_call.cloud_tasks import Dialer, DialListRow, save_dialer_list
from ccc.click_to_call.models import AssociateMasterList, AutoDialerList
from ccc.click_to_call.serializers import (AutoDialerListSerializer,
                                           AutoDialerMasterListSerializer)
from ccc.contacts.models import ContactGroup
from ccc.packages.models import TwilioNumber


@login_required
def get_token(request):
    """Returns a Twilio Client token"""
    # Create a TwilioCapability token with our Twilio API credentials
    ACCOUNT_SID = settings.TWILIO_SID
    AUTH_TOKEN = settings.TWILIO_TOKEN
    capability = ClientCapabilityToken(
        ACCOUNT_SID,
        AUTH_TOKEN)
    TWILIO_CLIENT_OUTGOING = settings.TWILIO_CLIENT_OUTGOING

    # Allow our users to make outgoing calls with Twilio Client
    capability.allow_client_outgoing(TWILIO_CLIENT_OUTGOING)

    # If the user is on the support dashboard page, we allow them to accept
    # incoming calls to "support_agent"
    # (in a real app we would also require the user to be authenticated)
    if request.GET.get('forPage') == "asdsad":
        capability.allow_client_incoming('support_agent')
    else:
        # Otherwise we give them a name of "customer"
        capability.allow_client_incoming('customer')

    # Generate the capability token
    token = capability.to_jwt()

    return HttpResponse(json.dumps({'token': token.decode('utf-8')}), content_type="application/json")


# @login_required


@csrf_exempt
def call(request):
    """Returns TwiML instructions to Twilio's POST requests"""
    # If the browser sent a phoneNumber param, we know this request
    # is a support agent trying to call a customer's phone
    dest_number = ''
    if 'PhoneNumber' in request.GET:
        dest_number = request.GET["PhoneNumber"]
    else:
        # This will raise a erro on twilio itself
        pass
    resp = VoiceResponse()
    from_no = request.GET["from_no"] if request.GET.get(
        "from_no") else "+441242305348"
    phones = TwilioNumber.objects.filter(twilio_number=from_no)
    if phones.exists():
        user = phones[0].user
    if user.balance.get('talktime', 0) <= 0:
        return HttpResponse("Error")
    max_duration = user.balance.get('talktime', 0) * 60
    callback_url = reverse("dial_callback",
                           kwargs={"twilio_number": from_no})
    with resp.dial(dest_number, caller_id=from_no, action=callback_url,
                   method="GET", time_limit=max_duration) as r:
        pass
    return HttpResponse(str(resp))


class ContactDialView(TemplateView):
    template_name = "ccc/click_to_call/call_contacts.html"

    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        campaigns = Campaign.objects.filter(user=request.user, active=True)
        groups = ContactGroup.objects.filter(user=request.user)
        phones = TwilioNumber.objects.filter(user=request.user).exclude(
            twilio_number__isnull=True,
            twilio_number='')
        context["phones"] = phones
        context["campaigns"] = campaigns
        context["groups"] = groups
        return self.render_to_response(context)


class DialPageView(TemplateView):
    template_name = "ccc/click_to_call/click_to_call.html"

    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        context["master_list_id"] = self.kwargs.get("master_list_id")
        phones = TwilioNumber.objects.filter(user=request.user)
        context["phones"] = phones
        return self.render_to_response(context)


class OptionPageView(TemplateView):
    template_name = "ccc/click_to_call/select_options.html"

    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)


class UploadedListView(TemplateView):
    template_name = "ccc/click_to_call/master_list.html"

    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)


class UploadListView(TemplateView):
    """
    """
    template_name = "ccc/click_to_call/upload_excel.html"

    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)


class UploadListOutputView(TemplateView):
    template_name = "ccc/click_to_call/upload_excel_output.html"

    def get_context_data(self, **kwargs):
        master_list = get_object_or_404(AssociateMasterList, id=kwargs['master_list_id'],
                                        user=self.request.user)
        kwargs['master_list'] = master_list
        valid_numbers = AutoDialerList.objects.filter(is_valid=True, associated_to=master_list)
        kwargs['total_numbers'] = valid_numbers.count()
        kwargs['total_landline'] = valid_numbers.filter(phone_type='landline').count()
        kwargs['total_cellphone'] = valid_numbers.filter(phone_type='cell-phone').count()
        kwargs['total_voip'] = valid_numbers.filter(phone_type='voip').count()

        if master_list.has_errors:
            unprocessed_numbers = AutoDialerList.objects.filter(is_valid=False, associated_to=master_list)
            kwargs['unprocessed_numbers'] = unprocessed_numbers
            kwargs['total_unprocessed_numbers'] = unprocessed_numbers.count()

        return kwargs

    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)


def validate_international_phonenumber(value):
    phone_number = to_python(value)
    if phone_number and not phone_number.is_valid():
        return False, u'The phone number entered is not valid.'
    return True, ''


class SaveUploadedListView(View):
    """
    """
    template_name = "ccc/click_to_call/upload_excel.html"

    def initialise_status_style(self, ):
        """Initialize excel styles
        """
        self.red_status_style = xlwt.XFStyle()
        self.red_status_style.font.bold = True
        self.red_pattern = xlwt.Pattern()
        self.red_status_style.font.colour_index = xlwt.Style.colour_map['red']
        self.red_status_style.pattern = self.red_pattern

        self.green_status_style = xlwt.XFStyle()
        self.green_status_style.font.bold = True
        self.green_pattern = xlwt.Pattern()
        self.green_status_style.font.colour_index = xlwt.Style.colour_map[
            'green']
        self.green_status_style.pattern = self.green_pattern

        self.orange_status_style = xlwt.XFStyle()
        self.orange_status_style.font.bold = True
        self.orange_pattern = xlwt.Pattern()
        self.orange_status_style.font.colour_index = xlwt.Style.colour_map[
            'orange']
        self.orange_status_style.pattern = self.orange_pattern

        self.grey_style = xlwt.XFStyle()
        self.grey_style.font.bold = True
        self.grey_style.font.colour_index = xlwt.Style.colour_map[
            'white']
        pattern = xlwt.Pattern()
        pattern.pattern = xlwt.Pattern.SOLID_PATTERN
        pattern.pattern_background_colour = xlwt.Style.colour_map['gray50']
        self.grey_style.pattern = pattern
        self.grey_style.alignment.horz = xlwt.Alignment.HORZ_CENTER_ACROSS_SEL

    def write_header(self, sheet_obj, header_data, row_position):
        """Method to set/update column names and width
        """
        column_position = 0
        row_position = 0
        for col_value, col_width in header_data.items():
            sheet_obj.col(column_position).width = col_width
            sheet_obj.write(row_position, column_position,
                            col_value, self.grey_style)
            column_position += 1

    def write_data_to_excel(self, sheet, row_data, row_no):
        """Method to write data to spreadsheet
        """
        style_map = {"fail": self.red_status_style,
                     }
        style = style_map["fail"]
        sheet.write(row_no, 0, row_data[0])
        sheet.write(row_no, 1, row_data[1])
        sheet.write(row_no, 2, row_data[2], style=style)

    def generate_excel(self, final_data):
        """Method to generate in excel format
        """
        spreadsheet = xlwt.Workbook(encoding="utf-8")
        sheet_obj = spreadsheet.add_sheet(
            "Sheet1", cell_overwrite_ok=True)

        header_data = OrderedDict([
            ('Phone', 256 * 25),
            ('Name(Optional)', 256 * 25),
            ('Error', 256 * 100),
        ])

        self.initialise_status_style()
        self.write_header(sheet_obj=sheet_obj,
                          header_data=header_data,
                          row_position=0)
        row_no = 1
        for data in final_data:
            self.write_data_to_excel(
                sheet=sheet_obj, row_data=data, row_no=row_no)
            row_no += 1

        fname = "contacts"
        response = HttpResponse(content_type="application/ms-excel")
        response[
            'Content-Disposition'] = 'attachment; filename="{}.xlsx"'.format(fname.strip())
        spreadsheet.save(response)
        return response

    def save_auto_dialer(self, name, final_data):
        """Save Autodialer Numbers
        """
        obj = AssociateMasterList.objects.create(
            name=name, user=self.request.user)
        for data in final_data:
            AutoDialerList.objects.create(number=data[0],
                                          name=data[1],
                                          associated_to=obj
                                          )

    @method_decorator(login_required)
    def post(self, request, *args, **kwargs):
        import xlrd

        file_obj = request.FILES.get("upload_file")
        s1 = xlrd.open_workbook(file_contents=file_obj.read())

        name = request.POST.get("list_name")
        sheet = s1.sheet_by_index(0)

        list_dialer = list()

        for rows in range(sheet.nrows):
            # if it's the first row... continue (sample row).
            if rows == 0:
                continue

            rows = DialListRow(sheet.row_values(rows))

            dialer = Dialer(rows.first_name, rows.last_name, rows.phone_number, rows.city, rows.state)
            list_dialer.append(dialer)

        m_list = AssociateMasterList.objects.create(name=name, user=request.user)
        # Async task
        task = save_dialer_list(m_list_id=m_list.id, dialers=list_dialer).execute()

        return HttpResponseRedirect(reverse('process_excel', args=[m_list.id, task.task_id]))


class ProcessUploadedFileView(TemplateView):
    """Check the status of task that process file uploaded"""
    template_name = "ccc/click_to_call/process_excel.html"

    def get_context_data(self, **kwargs):
        kwargs['ping_url'] = reverse('process_excel_status', args=[kwargs['task_id'], ])
        return kwargs

    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        #Asyn tasks #todo check status via gcloud #fixme implement status in gcloud library.
        # task_status = save_dialer_list(m_list_id=)
        #task_status = save_dialer_list.AsyncResult(context['task_id']).status
        # if task_status == 'SUCCESS':
        #     master_list = AssociateMasterList.objects.get(id=kwargs['master_list_id'])
        #     return HttpResponseRedirect(reverse('output_upload_excel', kwargs={'master_list_id': master_list.pk}))

        return self.render_to_response(context)


@login_required
def uploaded_file_status(request, task_id):
    #Fixme #todo , check if gcloud returns status
    return HttpResponse(json.dumps({
        'status': save_dialer_list.AsyncResult(task_id).status
    }), content_type="application/json")


class AutoDialNumberListView(generics.ListAPIView):
    """
    Keyword search for corporate.
    """
    queryset = AssociateMasterList.objects.all()
    serializer_class = AutoDialerMasterListSerializer
    paginate_by = 10

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(AutoDialNumberListView, self).dispatch(
            request, *args, **kwargs)

    def get_queryset(self, *args, **kwargs):
        return AssociateMasterList.objects.filter(
            user=self.request.user)


class AutoDialNumberView(generics.ListAPIView):
    """
    Keyword search for corporate.
    """
    queryset = AutoDialerList.objects.all()
    serializer_class = AutoDialerListSerializer
    paginate_by = 10

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(AutoDialNumberView, self).dispatch(
            request, *args, **kwargs)

    def get_queryset(self, *args, **kwargs):
        self.dailer_list_id = self.kwargs["dailer_list_id"]
        return AutoDialerList.objects.filter(associated_to=self.dailer_list_id,
                                             is_valid=True,
                                             associated_to__user=self.request.user)


class DialCallBackView(View):
    """Class to handle auto dial callback from twilio
    """

    def get(self, *args, **kwargs):
        """
        """
        call_duration = self.request.GET.get("DialCallDuration", 0)
        call_duration_in_mins = ceil(float(call_duration) / 60.0)
        twilio_number = kwargs["twilio_number"]
        queryset = TwilioNumber.objects.filter(twilio_number=twilio_number)
        if queryset.exists():
            twilio_obj = queryset[0]
            user = twilio_obj.user
            from ccc.packages.models import Credit
            credits_qs = Credit.objects.filter(package__user=user)
            if credits_qs.exists():
                credit_obj = credits_qs.latest("id")
                credit_obj.talktime = credit_obj.talktime - call_duration_in_mins
                credit_obj.save()
        return HttpResponse("Done")
