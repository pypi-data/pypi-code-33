from django.core.paginator import Paginator
from django.db.models import Count
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views import View
from django.views.generic import TemplateView

from ccc.campaigns.utils.shortcut import url_all_time_clicks
from ccc.common.mixins import LoginRequiredMixin
from ccc.contacts.models import Contact
from ccc.packages.decorators import check_user_subscription
from ccc.survey.models import Survey, SurveyLink, UserAnswer


class SurveysListView(TemplateView):
    """Listing all active surveys."""
    template_name = 'crm/marketing/surveys/survey_list.html'

    @method_decorator(check_user_subscription)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(SurveysListView, self).get_context_data(**kwargs)
        context['nav_title'] = 'My surveys'
        context['marketing'] = True
        return context


class SurveysAllView(TemplateView):
    """Listing all surveys, surveys actives and surveys archived."""
    template_name = 'crm/marketing/surveys/survey_list.html'

    @method_decorator(check_user_subscription)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(SurveysAllView, self).get_context_data(**kwargs)
        context['nav_title'] = 'Surveys'
        context['marketing'] = True
        return context


class SurveyDetailView(TemplateView):
    """Show details / questions of a specific survey."""
    template_name = 'crm/marketing/surveys/survey_detail.html'

    @method_decorator(check_user_subscription)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(SurveyDetailView, self).get_context_data(**kwargs)
        survey = get_object_or_404(Survey, pk=kwargs.get('pk'))
        context['nav_title'] = survey.title
        context['survey'] = survey
        context['marketing'] = True
        return context


class SurveyKeywordsView(TemplateView):
    template_name = 'crm/marketing/surveys/keywords.html'

    @method_decorator(check_user_subscription)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(SurveyKeywordsView, self).get_context_data(**kwargs)
        context['nav_title'] = 'Survey Keywords'
        context['marketing'] = True
        return context


class SurveyResponsesView(TemplateView):
    template_name = 'crm/marketing/surveys/responses.html'

    @method_decorator(check_user_subscription)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_survey_links(self, survey):
        links_query = SurveyLink.objects.all()
        if survey:
            links_query = SurveyLink.objects.filter(
                question__survey_id=survey)

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

        return short_links

    def get_user_answers(self, survey):
        qs = UserAnswer.objects.filter(
            question__survey__user=self.request.user
        )

        if survey:
            survey_obj = get_object_or_404(Survey, pk=survey)
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

        return results

    def get_context_data(self, **kwargs):
        context = super(SurveyResponsesView, self).get_context_data(**kwargs)
        context['surveys'] = Survey.objects.filter(user=self.request.user)
        context['survey'] = None
        survey = self.request.GET.get('survey', '0')
        context['survey'] = int(survey)
        context['short_links'] = self.get_survey_links(context['survey'])
        object_list = self.get_user_answers(context['survey'])
        p = Paginator(object_list, 50)
        page = self.request.GET.get('page')
        object_list = p.get_page(page)
        context['object_list'] = object_list
        context['nav_title'] = 'Survey Responses'
        context['marketing'] = True
        return context


class SurveyURLClicks(LoginRequiredMixin, TemplateView):
    template_name = "crm/marketing/surveys/urlclicks.html"

    @method_decorator(check_user_subscription)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(SurveyURLClicks, self).get_context_data(**kwargs)
        context['nav_title'] = 'Survey URL Clicks'
        context['marketing'] = True
        url = self.request.GET.get('url', None)
        query = SurveyLink.objects.filter(
            question__survey__user=self.request.user,
        )
        if url:
            query = query.filter(
                long_url=url
            )
        survey_links = query.values('question__survey__title', 'long_url',
                                    'contact__phone', 'short_url')
        for sl in survey_links:
            long_url, sl['clicks'] = url_all_time_clicks(sl.get('short_url'))
        context['survey_links'] = survey_links
        return context


class SurveyResponseContactView(LoginRequiredMixin, TemplateView):
    template_name = 'crm/marketing/surveys/contact-response.html'

    @method_decorator(check_user_subscription)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(SurveyResponseContactView, self).get_context_data(**kwargs)
        contact = get_object_or_404(Contact, pk=self.kwargs.get('pk'))
        survey = None
        if self.request.GET.get('survey', None):
            survey = get_object_or_404(Survey, pk=self.request.GET.get('survey'))
        q = UserAnswer.objects.filter(
            question__survey__user=self.request.user,
            contact=contact
        ).order_by("-created")
        if survey:
            q = q.filter(question__survey=survey)
        context['contact'] = contact
        context['survey'] = survey
        context['answers'] = q
        context['nav_title'] = '{}\'s Survey Responses'.format(contact.first_name)
        context['marketing'] = True
        return context


class SurveyResponsesDownloadView(LoginRequiredMixin, View):

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
