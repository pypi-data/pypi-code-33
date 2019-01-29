"""
Here all views only related to marketing:autodialer.
Remember protected views that required subscription, do this using the: check_user_subscription decorator.
"""
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.generic import TemplateView
from xlrd import XLRDError

from ccc.click_to_call.cloud_tasks import Dialer, DialListRow, save_dialer_list
from ccc.click_to_call.models import AssociateMasterList, AutoDialerList
from ccc.packages.decorators import check_user_subscription


class DialNumberView(LoginRequiredMixin, TemplateView):
    template_name = 'crm/marketing/autodialer/autodialer.html'

    @method_decorator(check_user_subscription)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(DialNumberView, self).get_context_data(**kwargs)
        context['nav_title'] = 'Dial Number'
        context['dialer'] = True
        return context


class DialContactsView(LoginRequiredMixin, TemplateView):
    template_name = 'crm/marketing/autodialer/autodialer-contacts.html'

    @method_decorator(check_user_subscription)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(DialContactsView, self).get_context_data(**kwargs)
        context['nav_title'] = 'Dial Contact'
        context['dialer'] = True
        return context


class DialMasterListView(LoginRequiredMixin, View):
    template_name = 'crm/marketing/autodialer/autodialer-masterlist.html'

    @method_decorator(check_user_subscription)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_context(self):
        context = dict()
        context['nav_title'] = 'Autodialer Masterlist'
        context['dialer'] = True
        return context

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, self.get_context())

    def post(self, request, *args, **kwargs):
        import xlrd

        file_obj = request.FILES.get("dial_list")
        name = request.POST.get("list_name")
        if not file_obj or not name:
            return render(request, self.template_name, context={'error': 'All fields are compulsory'})

        try:
            s1 = xlrd.open_workbook(file_contents=file_obj.read())
        except XLRDError as x:
            context = self.get_context()
            context.update({'error': str(x).split(':')[0]})
            return render(request, self.template_name, context)

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
        save_dialer_list(m_list_id=m_list.id, dialers=list_dialer).execute()

        return redirect(reverse('srm:marketing:autodialer:master-list-detail', kwargs={'pk': m_list.id}))


class DialMasterListDetailView(LoginRequiredMixin, TemplateView):
    template_name = 'crm/marketing/autodialer/autodialer-masterlist-detail.html'

    @method_decorator(check_user_subscription)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(DialMasterListDetailView, self).get_context_data(**kwargs)
        master_list = get_object_or_404(AssociateMasterList, pk=self.kwargs.get('pk'))
        context['nav_title'] = master_list.name
        context['dialer'] = True

        master_list = get_object_or_404(AssociateMasterList, id=kwargs['pk'],
                                        user=self.request.user)
        context['master_list'] = master_list
        valid_numbers = AutoDialerList.objects.filter(is_valid=True, associated_to=master_list)
        context['total_numbers'] = valid_numbers.count()
        context['total_landline'] = valid_numbers.filter(phone_type='landline').count()
        context['total_cellphone'] = valid_numbers.filter(phone_type='cell-phone').count()
        context['total_voip'] = valid_numbers.filter(phone_type='voip').count()

        if master_list.has_errors:
            unprocessed_numbers = AutoDialerList.objects.filter(is_valid=False, associated_to=master_list)
            context['unprocessed_numbers'] = unprocessed_numbers
            context['total_unprocessed_numbers'] = unprocessed_numbers.count()

        return context


class DialMasterListStatusView(LoginRequiredMixin, TemplateView):
    template_name = 'crm/marketing/autodialer/autodialer-masterlist-status.html'

    @method_decorator(check_user_subscription)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(DialMasterListStatusView, self).get_context_data(**kwargs)
        master_list = get_object_or_404(AssociateMasterList, pk=self.kwargs.get('pk'))
        context['nav_title'] = master_list.name
        context['dialer'] = True

        master_list = get_object_or_404(AssociateMasterList, id=kwargs['pk'],
                                        user=self.request.user)
        context['master_list'] = master_list
        valid_numbers = AutoDialerList.objects.filter(is_valid=True, associated_to=master_list)
        context['total_valid_numbers'] = valid_numbers.count()
        context['total_landline'] = valid_numbers.filter(phone_type='landline').count()
        context['total_cellphone'] = valid_numbers.filter(phone_type='cell-phone').count()
        context['total_voip'] = valid_numbers.filter(phone_type='voip').count()

        unprocessed_numbers = 0
        if master_list.has_errors:
            unprocessed_numbers = AutoDialerList.objects.filter(is_valid=False, associated_to=master_list)
            context['unprocessed_numbers'] = unprocessed_numbers
            context['total_unprocessed_numbers'] = unprocessed_numbers.count()

        context['total_numbers'] = valid_numbers.count() + unprocessed_numbers.count()

        return context


class PersonalizedMessagesView(TemplateView):
    template_name = 'crm/marketing/autodialer/personalized-messages.html'

    @method_decorator(check_user_subscription)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(PersonalizedMessagesView, self).get_context_data(**kwargs)
        context['nav_title'] = 'Your Personalized Messages'
        context['dialer'] = True
        return context
