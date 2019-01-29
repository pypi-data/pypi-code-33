import logging
import random
import string
from base64 import b64decode

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.messages.views import SuccessMessageMixin
from django.core.files.base import ContentFile
from django.db.models.aggregates import Count
from django.http import HttpResponse, HttpResponseRedirect
from django.http.response import Http404
from django.shortcuts import get_object_or_404, render
from django.urls import reverse, reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View
from django.views.generic.detail import DetailView
from django.views.generic.edit import (CreateView, DeleteView, FormView,
                                       UpdateView)
from django.views.generic.list import ListView
from extra_views import (CreateWithInlinesView, InlineFormSet,
                         UpdateWithInlinesView)
from rest_framework import generics, status, viewsets
from rest_framework.response import Response
from twilio.twiml.messaging_response import MessagingResponse
from twilio.twiml.voice_response import VoiceResponse

from ccc.campaigns.models import OSMS, Campaign, RejectedNumber
from ccc.campaigns.utils.shortcut import url_all_time_clicks
from ccc.common.mixins import LoginRequiredMixin
from ccc.contacts.models import Contact
from ccc.packages.models import TwilioNumber
from ccc.packages.utils import get_phone_number
from ccc.phone.number import PhoneNumber, TwilioPhoneNumber
from ccc.survey.cloud_tasks import survey_convert_audio_format
from ccc.survey.forms import (AssignKwywordsToSurveyForm, QuestionForm,
                              SurveyForm)
from ccc.survey.models import (AnswerChoice, McqAnswer, Question, Survey,
                               SurveyLink, SurveyMappedKeywords, TextAnswer,
                               UserAnswer)
from ccc.survey.serializers import SurveyAppSerializer, SurveyKeywordSerializer
from ccc.survey.survey import PhoneSurvey

logger = logging.getLogger(__name__)


class SurveyCreate(SuccessMessageMixin, LoginRequiredMixin, CreateView):
    """Create survey"""
    template_name = 'ccc/survey/survey_form.html'
    model = Survey
    success_message = "%(title)s Survey created successfully"
    form_class = SurveyForm

    def get_form(self, form_class=None):
        form = super(SurveyCreate, self).get_form(form_class)
        form.fields['phone'].queryset = get_phone_number(self.request.user)
        form.fields['phone'].required = True
        form.fields['campaign'].queryset = Campaign.objects.filter(
            user=self.request.user,
            active=True)
        return form

    def form_valid(self, form):
        survey = form.save(commit=False)
        survey.user = self.request.user
        survey.save()

        twilio_number = form.instance.phone
        twilio_number.in_use = True
        twilio_number.save()

        survey.update_twilio_urls()

        recording_saved = False
        if form.cleaned_data.get('voice_greeting_type', None) == 'voice_greeting_record':
            try:
                audio_data = b64decode(
                    form.cleaned_data.get('voice_greeting_original_recording', None).split(',')[1])
            except (IndexError, TypeError):
                pass  # invalid format?
            else:
                filename = 'rec_' + \
                           ''.join(
                               random.sample(string.ascii_lowercase + string.digits, 10)) + '.wav'
                survey.voice_greeting_original = ContentFile(
                    audio_data, filename)
                survey.save()
                recording_saved = True

        voice_greeting = form.cleaned_data["voice_greeting_original"]

        if voice_greeting or recording_saved:
            # async task
            survey_convert_audio_format(survey_id=survey.id).execute()

        return super(SurveyCreate, self).form_valid(form)

    def get_context_data(self, **kwargs):
        kwargs['form'] = self.get_form(self.form_class)
        context = super(SurveyCreate, self).get_context_data(**kwargs)
        context['form_name'] = 'Create Survey'
        return context

    def get_success_url(self):
        return reverse('survey_detail', args=[self.object.pk])


class Surveys(LoginRequiredMixin, ListView):
    template_name = 'ccc/survey/survey_list.html'
    model = Survey

    def get_queryset(self):
        qs = super(Surveys, self).get_queryset()
        return qs.filter(user=self.request.user, active=True)


class SurveysAll(LoginRequiredMixin, ListView):
    template_name = 'ccc/survey/survey_list.html'
    model = Survey

    def get_queryset(self):
        qs = super(SurveysAll, self).get_queryset()
        return qs.filter(user=self.request.user)


class SurveyDetail(LoginRequiredMixin, DetailView):
    """Survey details"""
    model = Survey
    template_name = 'ccc/survey/survey_detail.html'

    def get_queryset(self):
        qs = super(SurveyDetail, self).get_queryset()
        return qs.filter(user=self.request.user)


class SurveyArchive(LoginRequiredMixin, View):

    def post(self, request, pk, *args, **kwargs):

        try:
            survey = get_object_or_404(Survey, pk=pk)
            phone = survey.phone
            survey.archived()

            messages.success(
                self.request, 'Survey "%s" has been archvied and phone %s has been released successfully.' %
                              (survey.title, phone.twilio_number))

            return HttpResponseRedirect(reverse('survey_list'))
        except Exception as ex:
            logger.exception('SurveyArchive exception {}'.format(ex))
            return HttpResponseRedirect(reverse('survey_list'))


class SurveyUnArchive(SuccessMessageMixin, LoginRequiredMixin, UpdateView):
    template_name = "ccc/survey/survey_form.html"
    model = Survey
    fields = ['phone']
    success_message = "Survey unarchived successfully"

    def get_form(self, form_class=None):
        form = super(SurveyUnArchive, self).get_form(form_class)
        form.fields['phone'].queryset = TwilioNumber.objects.filter(
            user=self.request.user,
            in_use=False)
        form.fields['phone'].required = True
        return form

    def form_valid(self, form):
        survey = form.save(commit=False)
        survey.active = True
        survey.update_twilio_urls()
        return super(SurveyUnArchive, self).form_valid(form)

    def get_context_data(self, **kwargs):
        kwargs['form'] = self.get_form(self.form_class)
        context = super(SurveyUnArchive, self).get_context_data(**kwargs)
        context['form_name'] = 'Unarchive Survey > %s' % self.object.title
        return context

    def get_success_url(self):
        return reverse('survey_list')


class SurveyUpdate(SuccessMessageMixin, LoginRequiredMixin, UpdateView):
    model = Survey
    success_message = "%(title)s updated successfully"
    form_class = SurveyForm
    template_name = 'ccc/survey/survey_form.html'

    def get_form(self, form_class=None):
        form = super(SurveyUpdate, self).get_form(form_class)
        form.fields['phone'].queryset = get_phone_number(self.request.user, survey=self.object)
        form.fields['phone'].required = True
        form.fields['campaign'].queryset = Campaign.objects.filter(user=self.request.user, active=True)
        return form

    def form_valid(self, form):
        saved_instance = get_object_or_404(Survey, pk=self.object.id)
        survey = form.save(commit=False)
        survey.active = True

        if saved_instance.phone != form.instance.phone:

            twilio_number = form.instance.phone
            twilio_number.in_use = True
            twilio_number.save()

            # release the previously used number
            if saved_instance.phone:
                saved_instance.phone.in_use = False
                saved_instance.phone.save()
                saved_instance.phone.update_twilio_urls_to_default()

            survey.update_twilio_urls()

        recording_saved = False
        if form.cleaned_data.get('voice_greeting_type', None) == 'voice_greeting_record':
            try:
                audio_data = b64decode(
                    form.cleaned_data.get('voice_greeting_original_recording', None).split(',')[1])
            except (IndexError, TypeError):
                pass  # invalid format?
            else:
                filename = 'rec_' + \
                           ''.join(
                               random.sample(string.ascii_lowercase + string.digits, 10)) + '.wav'
                survey.voice_greeting_original = ContentFile(
                    audio_data, filename)
                survey.save()
                recording_saved = True

        voice_greeting = form.cleaned_data["voice_greeting_original"]

        if voice_greeting or recording_saved:
            # async task
            survey_convert_audio_format(survey_id=survey.id).execute()

        return super(SurveyUpdate, self).form_valid(form)

    def get_context_data(self, **kwargs):
        kwargs['form'] = self.get_form(self.form_class)
        context = super(SurveyUpdate, self).get_context_data(**kwargs)
        context['form_name'] = 'Update Survey > %s' % self.object.title
        return context

    def get_success_url(self):
        return reverse('survey_list')


class SurveyResponse(LoginRequiredMixin, ListView):
    template_name = "ccc/survey/survey_response.html"

    def dispatch(self, request, *args, **kwargs):
        self.contact = get_object_or_404(Contact, pk=self.kwargs.get('pk'))
        self.survey = None
        if request.GET.get('survey', None):
            self.survey = get_object_or_404(
                Survey, pk=request.GET.get('survey'))
        return super(SurveyResponse, self).dispatch(request, *args, **kwargs)

    def get_queryset(self):
        q = UserAnswer.objects.filter(
            question__survey__user=self.request.user,
            contact=self.contact
        ).order_by("-created")
        if self.survey:
            q = q.filter(question__survey=self.survey)
        return q


class AnswerChoicesInlineAdd(InlineFormSet):
    model = AnswerChoice
    exclude = ('code',)
    factory_kwargs = {
        'extra': 2,
    }


class AnswerChoicesInlineUpdate(InlineFormSet):
    model = AnswerChoice
    exclude = ('code',)
    factory_kwargs = {
        'extra': 0,
    }


class QuestionCreate(CreateWithInlinesView):
    model = Question
    form_class = QuestionForm
    template_name = 'ccc/survey/question_form.html'

    success_message = "%(question)s created successfully"
    inlines = [AnswerChoicesInlineAdd]
    survey = None
    in_response_of = []
    in_response_of_question = []

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        self.survey = get_object_or_404(Survey, pk=kwargs.get('survey_pk'), user=self.request.user)

        type_ = kwargs.get('type', None)

        if type_:
            if kwargs.get('pk', None) and type_ == 'mcq':
                answer_choice = get_object_or_404(AnswerChoice, pk=kwargs.get('pk'))
                if self.request.method == 'POST' and self.request.POST.get('add-to-all'):
                    self.in_response_of = answer_choice.question.answer_choices.all()
                else:
                    self.in_response_of = [answer_choice]

            elif kwargs.get('pk', None) and type_ == 'q':
                question = get_object_or_404(Question, pk=kwargs.get('pk'))
                self.in_response_of_question = [question]

        else:  # When user has not specified where to insert the question
            question = self.survey.questions.last_question()
            if self.request.method == 'POST' and self.request.POST.get('add-to-all'):
                self.in_response_of = []

            elif question and question.question_type == Question.TYPES.text:
                self.in_response_of_question = [question]

            elif question and question.question_type == Question.TYPES.mcq:
                self.in_response_of = question.answer_choices.all()

        return super(QuestionCreate, self).dispatch(request, *args, **kwargs)

    def forms_valid(self, form, inlines):
        self.object = form.save(commit=False)
        self.object.survey = self.survey
        self.object.save()

        for question in self.in_response_of:
            self.object.in_response_of.add(question)

        for question in self.in_response_of_question:
            self.object.in_response_of_question.add(question)

        messages.success(self.request, self.success_message % {'question': self.object.question})

        return super(QuestionCreate, self).forms_valid(form, inlines)

    def get_context_data(self, **kwargs):
        context = super(QuestionCreate, self).get_context_data(**kwargs)

        if self.in_response_of:
            title = 'Add followup question to %s' % self.in_response_of[0].question

        elif self.in_response_of_question:
            title = 'Add followup question to %s' % self.in_response_of_question[0].question

        else:
            title = 'Add question to survey'

        context['form_name'] = title
        context['survey'] = self.survey

        return context

    def get_success_url(self):
        return reverse('survey_detail', args=[self.survey.pk])


class QuestionUpdate(LoginRequiredMixin, UpdateWithInlinesView):
    template_name = 'ccc/survey/question_form.html'
    model = Question
    form_class = QuestionForm
    success_message = "%(question)s updated successfully"
    inlines = [AnswerChoicesInlineUpdate]
    survey = None
    extra = 0

    def dispatch(self, *args, **kwargs):
        self.survey = get_object_or_404(
            Survey,
            questions__id=kwargs.get('pk'),
            user=self.request.user)
        return super(QuestionUpdate, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(QuestionUpdate, self).get_context_data(**kwargs)
        context['form_name'] = 'Update Question'
        context['survey'] = self.survey
        return context

    def get_success_url(self):
        return reverse('survey_detail', args=[self.survey.pk])

    def get_initial(self):
        """Get initial form values. Updating survey questions"""
        return {
            'schedular_step': self.object.schedular_step,
            'delay': self.object.delay_value
        }


class QuestionDelete(SuccessMessageMixin, LoginRequiredMixin, DeleteView):
    model = Question

    def get_success_url(self):
        return reverse('survey_detail', args=[self.object.survey.pk])


class TwilioSMSHandler(View):

    @csrf_exempt
    def dispatch(self, *args, **kwargs):
        return super(TwilioSMSHandler, self).dispatch(*args, **kwargs)

    @classmethod
    def trigger_survey(cls, from_, to, body, manual_trigger=False, lead_type=7):
        """Internal function to validate and trigger survey
        """
        resp = MessagingResponse()
        reject_numbers = RejectedNumber.objects.filter(reject_number=from_)
        is_reject = False
        if reject_numbers.exists():
            reject_number = reject_numbers[0]
            if reject_number.reject_for_all:
                is_reject = True
            elif reject_number.twilio_numbers.filter(twilio_number=to).exists():
                is_reject = True
        if is_reject:
            resp = VoiceResponse()
            resp.reject("busy")
            return HttpResponse(resp, content_type='application/xml')

        twilio_number = get_object_or_404(TwilioNumber, twilio_number=to)
        user = twilio_number.user

        surveys = Survey.objects.filter(phone=twilio_number)
        keyword_trigger = False
        # HotFix if we don`t recevie survey object
        # ToDo
        survey = surveys.first()

        if surveys:
            mapped_keyword = SurveyMappedKeywords.objects.filter(
                survey__in=surveys,
                keyword__iexact=str(body).lower().strip(),
                is_active=True)
            if mapped_keyword.exists():
                survey = mapped_keyword[0].survey
                keyword_trigger = True
            else:
                query = Contact.objects.filter(phone=from_, user=user)
                survey = surveys.first()
                if query.exists():
                    record = query[0]
                    survey = record.survey if record.survey else survey

        try:
            contact, created = Contact.objects.get_or_create(
                phone=from_,
                user=user,
                defaults={
                    'lead_type': lead_type
                }
            )
            contact.survey = survey
            contact.save()
        except Contact.MultipleObjectsReturned:
            contact = Contact.objects.filter(
                phone=from_,
                user=user).first()

        if survey.campaign:
            contact.campaigns.add(survey.campaign)

        if keyword_trigger:
            root_question = survey.questions.root_question()
            if root_question and user.balance.get('sms', 0) > 0:
                OSMS.objects.create(
                    from_no=to,
                    to=from_,
                    text=root_question.get_message(contact),
                    countdown=root_question.delay)
                message = 'Thank you for starting the survey with keyword'
                # Disabled this as per client request
                #                 resp.message(message)
                return HttpResponse(resp, content_type='application/xml')

        # current question
        question = survey.questions.question_for_contact(survey, contact)

        if not question:
            if survey.last_message:
                message = survey.last_message
            else:
                message = 'No more questions for you. Thanks!'

            resp.message(message)
            return HttpResponse(resp, content_type='application/xml')

        if manual_trigger and question and user.balance.get('sms', 0) > 0:
            OSMS.objects.create(
                from_no=to,
                to=from_,
                text=question.get_message(contact),
                countdown=question.delay)
            return

        if question.question_type == Question.TYPES.mcq:
            # validate answer
            try:
                answer_code = int(body.strip())
            except ValueError:
                message = "Please respond with a valid choice.\n"
                message += question.get_message(contact)
                resp.message(message)
                return HttpResponse(resp, content_type='application/xml')
            else:
                answers = question.answer_choices.filter(code=answer_code)
                if answers.count() != 1:
                    message = "Please respond with a valid choice.\n"
                    message += question.get_message(contact)
                    resp.message(message)
                    return HttpResponse(resp, content_type='application/xml')
                answer = answers[0]

                # valid answer. record it
                McqAnswer.objects.get_or_create(
                    answer_choice=answer, contact=contact, question=question)
        elif question.question_type == Question.TYPES.text:
            TextAnswer.objects.get_or_create(
                question=question, contact=contact,
                defaults={
                    'answer': body.strip()
                })
            # Update the contact with the response field
            if question.contact_mapping:
                setattr(contact, question.contact_mapping, body.strip())
                contact.save()

        # ask next question if any
        next_question = survey.questions.question_for_contact(
            survey, contact)

        if next_question and user.balance.get('sms', 0) > 0:
            OSMS.objects.create(
                from_no=to,
                to=from_,
                text=next_question.get_message(contact),
                countdown=question.delay)

        else:
            if survey.last_message:
                message = survey.last_message
            else:
                message = 'No more questions for you. Thanks!'
            resp.message(message)

        return HttpResponse(resp, content_type='application/xml')

    def post(self, request):
        from_ = request.POST.get("From", '')
        to = request.POST.get("To", '')
        body = request.POST.get("Body", '')
        return TwilioSMSHandler.trigger_survey(from_=from_, to=to, body=body)


class TwilioCallHandler(View):
    """
    Call Handler - received/handle a twillio "voice" webhook signal.
    """

    @csrf_exempt
    def dispatch(self, *args, **kwargs):
        return super(TwilioCallHandler, self).dispatch(*args, **kwargs)

    def post(self, request):
        caller = PhoneNumber(request.POST.get("From", ''))
        twilio_phone = TwilioPhoneNumber(request.POST.get("To", ''))

        resp = VoiceResponse()

        if caller.is_reject(twilio_phone):
            resp.reject("busy")
            return HttpResponse(resp, content_type='application/xml')

        if twilio_phone.redirect:
            resp.dial(twilio_phone.redirect_number.to_no)
            return HttpResponse(resp, content_type='application/xml')

        survey = PhoneSurvey(twilio_phone)

        if not survey.exists():
            resp.say("Thank you. Leave a message after the tone")
            resp.record(maxLength="120", action="/handle-recording/")
            return HttpResponse(resp, content_type='application/xml')

        contact = survey.create_contact(caller)

        survey.add_campaign(contact)
        survey.send_sms(contact, caller.number)

        # Play the audio
        if survey.voice_greeting:
            resp.play(survey.voice_greeting_url)
        elif survey.greeting_text:
            resp.say(survey.greeting_text)
        else:
            resp.say("Thank you for calling us.")

        return HttpResponse(resp, content_type='application/xml')


class Dashboard(LoginRequiredMixin, View):
    template_name = "ccc/survey/dashboard.html"

    def get(self, request):
        context = {}
        context['surveys'] = Survey.objects.filter(user=self.request.user)
        context['survey'] = None
        survey = self.request.GET.get('survey', '0')
        try:
            context['survey'] = int(survey)
        except BaseException:
            pass

        links_query = SurveyLink.objects.all()
        if context['survey']:
            links_query = SurveyLink.objects.filter(
                question__survey_id=context['survey'])

        short_links = links_query.order_by('long_url').filter(
            question__survey__user=self.request.user).values(
            'long_url', 'question_id',
            'question__survey__title'
        ).annotate(
            total=Count('long_url'))

        for link in short_links:
            long_url = link.get('long_url', None)
            question_id = link.get('question_id', None)
            link['clicks'] = 0
            if long_url and question_id:
                survey_links = SurveyLink.objects.filter(long_url=long_url)
                for sl in survey_links:
                    if question_id == sl.question.pk:
                        long_url, clicks = url_all_time_clicks(sl.short_url)
                        link['clicks'] += int(clicks)

        context['short_links'] = short_links

        qs = UserAnswer.objects.filter(
            question__survey__user=self.request.user
        )

        if context['survey']:
            survey_obj = get_object_or_404(Survey, pk=context['survey'])
            qs = qs.filter(question__survey=survey_obj)

        results = qs.values(
            'question__survey__title',
            'question__survey__pk',
            'contact__phone',
            'contact__pk'
        ).order_by(
            'contact__pk'
        ).annotate(
            num_answers=Count('contact__pk')
        )

        context['object_list'] = results

        return render(request, self.template_name, context)


class LinkClicks(LoginRequiredMixin, View):
    template_name = "ccc/survey/survey_url_clicks.html"

    def get(self, request):
        url = request.GET.get('url', None)
        query = SurveyLink.objects.filter(
            question__survey__user=request.user,
        )
        if url:
            query = query.filter(
                long_url=url
            )
        survey_links = query.values('question__survey__title', 'long_url',
                                    'contact__phone', 'short_url')
        for sl in survey_links:
            long_url, sl['clicks'] = url_all_time_clicks(sl.get('short_url'))

        context = {
            'survey_links': survey_links
        }
        return render(request, self.template_name, context)


class AssignKwywordsToSurveyView(LoginRequiredMixin, FormView):
    """
    Update UnverifiedPhone of user
    """
    form_class = AssignKwywordsToSurveyForm
    template_name = 'ccc/campaigns/edit_campaign_keywords.html'
    success_url = reverse_lazy('list_keywords_to_campaign')
    success_message = "Keyword(s) was updated successfully"

    def get_initial(self):
        """
        Returns the initial data to use for forms on this view.
        """
        initial = super(AssignKwywordsToSurveyView, self).get_initial()
        survey_id = self.kwargs['survey_id']
        mapped_keywords = SurveyMappedKeywords.objects.filter(
            survey=survey_id,
            is_active=True).values_list('keyword', flat=True)
        mapped_keywords = ", ".join([str(x) for x in mapped_keywords])
        initial['keywords'] = mapped_keywords

        return initial

    def dispatch(self, *args, **kwargs):
        dispatch = super(AssignKwywordsToSurveyView, self).dispatch(
            *args, **kwargs)
        survey_id = self.kwargs['survey_id']
        user = self.request.user
        if not user.surveys.filter(id=survey_id, active=True).exists():
            from rest_framework import exceptions
            raise exceptions.PermissionDenied()
        return dispatch

    def get_form_kwargs(self):
        """
        Returns the keyword arguments for instantiating the form.
        """
        user = self.request.user
        survey_id = self.kwargs['survey_id']
        kwargs = {
            'initial': self.get_initial(),
            'prefix': self.get_prefix(),
            'user': user,
            'survey_id': survey_id
        }

        if self.request.method in ('POST', 'PUT'):
            kwargs.update({
                'data': self.request.POST,
                'files': self.request.FILES,
            })
        return kwargs

    def form_valid(self, form):
        """
        If the form is valid, redirect to the supplied URL.
        """
        form.save()
        messages.add_message(
            self.request, messages.SUCCESS, self.success_message)
        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form):
        """
        If the form is invalid, re-render the context data with the
        data-filled form and errors.
        """
        return self.render_to_response(self.get_context_data(form=form))


class SurveyKeywordAPIListView(generics.ListAPIView):
    """
    Keyword search for corporate.
    """
    queryset = SurveyMappedKeywords.objects.all()
    serializer_class = SurveyKeywordSerializer
    paginate_by = 10

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(SurveyKeywordAPIListView, self).dispatch(
            request, *args, **kwargs)

    def get_queryset(self, *args, **kwargs):
        surveys = self.request.user.surveys.filter(active=True)
        queryset = surveys
        return queryset


class SurveyResponseDownload(LoginRequiredMixin, View):
    template_name = "ccc/survey/survey_response.html"

    def insert_data_in_sheet(self, survey, sheets, xls_data):
        """Insert data in excel sheet"""
        answers = UserAnswer.objects.filter(question__survey=survey).order_by("-created")
        for answer in answers:
            created = str(answer.created.ctime())
            question = answer.question.question
            phone = answer.contact.phone
            usr_answer = ''
            if hasattr(answer, 'mcqanswer'):
                usr_answer = answer.mcqanswer.answer_choice.answer
            elif hasattr(answer, 'textanswer'):
                usr_answer = answer.textanswer.answer

            col_data = [created, phone, question, usr_answer]
            if not xls_data.get(phone):
                xls_data[phone] = []
            xls_data[phone].append(col_data)
        starting_posotion = 3
        for phone_key in xls_data.keys():
            for col_data in xls_data[phone_key]:
                for index, x in enumerate(col_data):
                    sheets.write(starting_posotion, index, col_data[index])
                starting_posotion += 1
            starting_posotion += 2

    def get(self, *args, **kwargs):
        import xlwt
        s1 = xlwt.Workbook(encoding="utf-8")
        if self.kwargs.get('id') == 'all':
            surveys = Survey.objects.filter(user=self.request.user)
        else:
            surveys = Survey.objects.filter(pk=self.kwargs.get('id'), user=self.request.user)
            if not surveys:
                raise Http404

        for survey in surveys:
            sheetname = str(survey.title) + ' ' + str(survey.pk)
            sheets = s1.add_sheet(sheetname, cell_overwrite_ok=True)
            first = ['Date created', 'Phone', 'Question', 'Answer']
            sheets.col(first.index('Date created')).width = 256 * 25
            sheets.col(first.index('Phone')).width = 256 * 20
            sheets.col(first.index('Question')).width = 256 * 50
            sheets.col(first.index('Answer')).width = 256 * 90
            style = xlwt.XFStyle()
            style.font.bold = True
            pattern = xlwt.Pattern()
            pattern.pattern = xlwt.Pattern.SOLID_PATTERN
            pattern.pattern_background_colour = xlwt.Style.colour_map['gray50']
            style.pattern = pattern
            style.alignment.horz = xlwt.Alignment.HORZ_CENTER_ACROSS_SEL
            for i, x in enumerate(first):
                sheets.write(2, i, first[i], style)
            sheets.write_merge(0, 0, 0, 3, survey.title, style=style)
            xls_data = {}
            self.insert_data_in_sheet(survey, sheets, xls_data)
        response = HttpResponse(content_type="application/ms-excel")
        response['Content-Disposition'] = 'attachment; filename="survey_response.xls"'
        s1.save(response)
        return response


class SurveyAppViewSet(viewsets.ModelViewSet):
    """
        Class for handling Movie request
    """
    serializer_class = SurveyAppSerializer
    model = Campaign
    queryset = Survey.objects.all()
    paginate_by = 10

    def list(self, request, *args, **kwargs):
        self.object_list = Survey.objects.filter(user=request.user,
                                                 active=True)
        page = self.paginate_queryset(self.object_list)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(self.object_list, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            survey = serializer.instance
            twilio_number = serializer.instance.phone
            twilio_number.in_use = True
            twilio_number.save()
            if self.request.FILES.get("voice_greeting_original_recording"):
                try:
                    audio_data = b64decode(request.FILES["voice_greeting_original_recording"])
                    filename = 'rec_{}.wav'.format(''.join(random.sample(string.ascii_lowercase + string.digits, 10)))
                    survey.voice_greeting_original = ContentFile(audio_data, filename)
                    survey.save()
                except Exception as ex:
                    error = {
                        "error": "Error occurred while audio conversion",
                        "exception": "{}".format(ex)
                    }
                    return Response(error, status=status.HTTP_400_BAD_REQUEST)

            self.object = serializer.save(force_insert=True)
            survey.update_twilio_urls()
            self.perform_create(serializer)

            if self.object.voice_greeting_original:
                # Async task
                survey_convert_audio_format(survey_id=survey.id).execute()
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED,
                            headers=headers)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
