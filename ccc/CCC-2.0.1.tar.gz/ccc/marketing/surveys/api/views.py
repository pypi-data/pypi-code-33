"""
API / Resources for Survey's API on Fusion APP.
"""
from urllib.parse import quote

from django.contrib.sites.models import Site
from django.db.models import Count, F
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status, viewsets
from rest_framework.authentication import (BasicAuthentication,
                                           SessionAuthentication)
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from twilio.twiml.voice_response import VoiceResponse

from ccc.contacts.models import Contact
from ccc.marketing.surveys.api.serializers import (AnswerChoiceSerializer,
                                                   MappedKeywordSerializer,
                                                   QuestionFilter,
                                                   QuestionSerializer,
                                                   SurveyFilter,
                                                   SurveyKeywordsSerializer,
                                                   SurveySerializer,
                                                   TriggerSurveySerializer,
                                                   UserAnswerSerializer, QuestionTreeViewSerializer,
                                                   ResortSurveyQuestionsSerializer)
from ccc.mixin import AuthParsersMixin, StandardResultsSetPagination
from ccc.phone.number import PhoneNumber, TwilioPhoneNumber
from ccc.survey.cloud_tasks import trigger_survey
from ccc.survey.models import AnswerChoice, McqAnswer, Question
from ccc.survey.models import Survey as SurveyModel
from ccc.survey.models import SurveyMappedKeywords, TextAnswer, UserAnswer
from ccc.survey.survey import PhoneSurvey
from django_filters.rest_framework import DjangoFilterBackend


class SurveyViewSet(AuthParsersMixin, viewsets.ModelViewSet):
    """
    Survey API View Set: /api/marketing/surveys/
    """
    queryset = SurveyModel.objects.all()
    serializer_class = SurveySerializer
    filter_class = SurveyFilter
    filter_backends = (DjangoFilterBackend,)

    def retrieve(self, request, pk=None):
        """Retrieve Survey details"""
        queryset = self.get_queryset()
        survey = get_object_or_404(queryset, pk=pk)
        serializer = self.serializer_class(survey)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def archived(self, request, pk=None):
        """
        Controller that allow to archived a survey: /api/marketing/surveys/{pk}/archive
        """
        try:
            survey = SurveyModel.objects.get(user=self.request.user, id=pk)
            survey.archived()
            return Response(self.serializer_class(survey).data)
        except Exception as e:
            # todo logger exception with sentry
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'])
    def unarchived(self, request, pk=None):
        """
        Controller that allow to archived a survey: /api/marketing/surveys/{pk}/unarchive
        """
        try:
            survey = SurveyModel.objects.get(user=self.request.user, id=pk)
            survey.un_archived()
            return Response(self.serializer_class(survey).data)
        except Exception as e:
            # todo logger exception with sentry
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'], url_name='questions')
    def questions(self, request, pk=None):
        """
        Controller, list all questions associated to the survey: /api/marketing/surveys/{pk}/questions/,
        You can set '?level=true' to sort by tree
        """
        survey = get_object_or_404(self.get_queryset(), pk=pk)

        # try:
        questions = Question.objects.filter(survey=survey).order_by('created')
        serializer = QuestionSerializer(questions, many=True)
        if request.query_params.get('level'):
            questions = questions.filter(in_response_of__isnull=True, in_response_of_question__isnull=True) \
                .order_by('order')
            serializer = QuestionTreeViewSerializer(questions, many=True)
        return Response(serializer.data)

        # except Exception as e:
        # todo logger exception with sentry
        # return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'], url_name='add-question')
    def add_question(self, request, pk=None):
        """
        Controller. Add questions to the survey: /api/marketing/surveys/{pk}/add_question
        """
        get_object_or_404(self.get_queryset(), pk=pk)
        question = QuestionSerializer(data=request.data)

        question.is_valid(raise_exception=True)
        question.save()
        return Response(question.data)

    def get_queryset(self):
        """
        Filter all surveys for the logged user (owner)
        """
        # Queryset associated always to the request owner.
        queryset = SurveyModel.objects.filter(user=self.request.user)

        is_active = self.request.query_params.get('active', None)

        if is_active is not None:
            lc_value = True if is_active.lower() == "true" else False
            queryset = queryset.filter(active=lc_value)

        return queryset

    def perform_create(self, serializer):
        survey = serializer.save()
        survey.phone.in_use = True
        survey.save()
        from ccc.survey.cloud_tasks import survey_convert_audio_format
        survey_convert_audio_format(survey_id=survey.id).execute()

    def perform_update(self, serializer):
        # Check if the phone number was changed
        old_phone_id = self.get_object().phone_id
        new_phone_id = serializer.validated_data.get('phone').id
        # We want to update phone if the phone number was changed
        if old_phone_id != new_phone_id:
            # If a phone number was attached before, update its survey twilio url to default
            if old_phone_id:
                self.get_object().phone.idle()
            survey = serializer.save()
            survey.phone.in_use = True
            survey.phone.save()
            survey.update_twilio_urls()
            from ccc.survey.cloud_tasks import survey_convert_audio_format
            survey_convert_audio_format(survey_id=survey.id).execute()
            return
        serializer.save()

    def perform_destroy(self, instance):
        if self.get_object().phone:
            self.get_object().phone.idle()
        instance.delete()


class QuestionsViewSet(viewsets.ModelViewSet):
    """
    Survey Questions API View set: /api/marketing/questions/
    """
    authentication_classes = (SessionAuthentication, BasicAuthentication)
    permission_classes = (IsAuthenticated,)
    serializer_class = QuestionSerializer
    filter_class = QuestionFilter

    def get_queryset(self):
        return Question.objects.filter(survey__user=self.request.user).order_by('created')

    @action(detail=True, methods=['get'], url_name='children', url_path='children')
    def question_children(self, request, **kwargs):
        queryset = self.get_queryset()
        queryset = queryset.filter(in_response_of_question=self.get_object())
        return Response(self.serializer_class(queryset, many=True).data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], url_name='resort', url_path='re-sort')
    def resort_questions(self, request, **kwargs):
        serializer = ResortSurveyQuestionsSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        new_order = serializer.data.get('order')
        for item in new_order:
            Question.objects.filter(pk=item.get('id')).update(order=item.get('order'))
        return Response({'status': 'success'}, status=status.HTTP_200_OK)


class AnswerChoiceViewSet(viewsets.ModelViewSet):
    """
    Survey Questions API View set: /api/marketing/questions/answer-options/
    """
    authentication_classes = (SessionAuthentication, BasicAuthentication)
    permission_classes = (IsAuthenticated,)
    queryset = AnswerChoice.objects.all()
    serializer_class = AnswerChoiceSerializer

    @action(detail=True, methods=['get'], url_name='questions')
    def questions(self, request, pk=None):
        """
        Controller, list all questions associated to the answer:
        /api/marketing/surveys/questions/answer-options/<pk>/questions/
        """
        questions = self.get_object().child_questions.all()
        serializer = QuestionSerializer(questions, many=True)
        return Response(serializer.data)


class ListQuestionsOptions(APIView):
    """
    Listing all the questions options  : /api/marketing/surveys/questions/options/
    (contact mapping fields, step schedular, etc).
    """
    authentication_classes = (SessionAuthentication, BasicAuthentication)
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        from ccc.survey.choices import QUESTION_SCHEDULAR_STEP
        from ccc.survey.models import Question

        options = {
            'schedular_step': QUESTION_SCHEDULAR_STEP,
            'contact_mapping': list(Question.CONTACT_MAPPINGS),
            'question_types': list(Question.TYPES),
        }

        return Response(options)


class MappedKeywordViewSet(ModelViewSet):
    """
        request data = {
            'survey': <survey_pk>,
            'keywords': [<keyword1>, <keyword2>, ... ]
        }

        response data = {
            'survey': {...}
            'keywords': [
                {...}
            ]
        }
    """

    def get_queryset(self):
        if self.request.method == 'GET':
            return SurveyModel.objects.filter(user=self.request.user, active=True,
                                              surveymappedkeywords__isnull=False).distinct()
        return SurveyMappedKeywords.objects.filter(survey__user=self.request.user).order_by('-created_at')

    pagination_class = StandardResultsSetPagination

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return SurveyKeywordsSerializer
        return MappedKeywordSerializer


class TriggerSurveyView(APIView):
    def post(self, request, survey_id):
        data = dict(self.request.data)
        data.update({'survey_id': survey_id})
        serializer = TriggerSurveySerializer(data=data)
        if serializer.is_valid(raise_exception=True):
            contact_ids = serializer.validated_data.get('contacts')
            group_ids = serializer.validated_data.get('groups')
            group_contacts = Contact.objects.filter(groups__in=group_ids).values_list('pk', flat=True)
            contact_ids += group_contacts
            trigger_survey(survey_id=survey_id, contact_ids=list(set(contact_ids))).execute()
        return Response({'success': True}, status=status.HTTP_200_OK)


class SurveyResponsesViewSet(ModelViewSet):
    def get_queryset(self):
        return UserAnswer.objects.filter(survey__user=self.request.user).order_by('contact__pk') \
            .annotate(num_answers=Count('contact__pk'))

    serializer_class = UserAnswerSerializer


@method_decorator(csrf_exempt, name='dispatch')
class GetSurveyGreetingsView(APIView):
    def get_response(self, from_):
        response_data = {'status': '', 'body': '', 'type': ''}
        # type = ('text', 'url')
        survey = PhoneSurvey(TwilioPhoneNumber(from_))
        if survey.voice_greeting:
            response_data.update({'status': 'success', 'type': 'url', 'content': survey.voice_greeting_url})
            return Response(response_data, status=status.HTTP_200_OK, content_type='application/json')
        elif survey.greeting_text:
            response_data.update({'status': 'success', 'type': 'text', 'content': survey.greeting_text})
            return Response(response_data, status=status.HTTP_200_OK, content_type='application/json')
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST, content_type='application/json')

    def get(self, request):
        return self.get_response(request.query_params.get('From'))


class GetSurveyFinalMessageView(APIView):
    def get(self, request):
        From = request.query_params.get('From')
        survey = PhoneSurvey(TwilioPhoneNumber(From))
        if survey.last_message:
            return Response(survey.last_message, status=status.HTTP_200_OK)
        else:
            return Response('Thanks for your time and responses.', status=status.HTTP_200_OK)


@method_decorator(csrf_exempt, name='dispatch')
class GetQuestionView(APIView):
    def get(self, request):
        response_data = {'status': '', 'body': '', 'type': ''}
        From = request.query_params.get('From')
        To = request.query_params.get('To')
        survey = PhoneSurvey(TwilioPhoneNumber(From))
        contact = Contact.objects.filter(phone=To).first()
        question = survey.get_next_question(contact)
        response_data.update({'status': 'empty'})
        if question:
            response_data.update({'status': 'success', 'body': question.question, 'type': question.question_type})
            if question.question_type == 'mcq':
                response_data.update({'options': AnswerChoiceSerializer(question.answer_choices.order_by('pk'),
                                                                        many=True).data})
        return Response(response_data, status=status.HTTP_200_OK)


@method_decorator(csrf_exempt, name='dispatch')
class SubmitAnswerView(View):
    def save_text_answer(self, question, contact, answer):
        TextAnswer.objects.get_or_create(question=question, contact=contact, answer=answer)

    def save_mcq_answer(self, question, contact, answer):
        # Sort in same order as they were sent to call
        options = question.answer_choices.order_by('pk')
        answer_chosen = options[int(answer) - 1]
        McqAnswer.objects.get_or_create(question=question, contact=contact, answer_choice=answer_chosen)

    def post(self, request):
        From = request.POST.get('From')
        To = request.POST.get('To')
        answer = request.POST.get('answer')
        survey = PhoneSurvey(TwilioPhoneNumber(From))
        contact = Contact.objects.filter(phone=To).first()
        question = survey.get_next_question(contact)
        # If a question's response is to be filled in the contact's profile
        if question.contact_mapping:
            setattr(contact, question.contact_mapping, answer)
            contact.save()
        if question.question_type == 'mcq':
            self.save_mcq_answer(question, contact, answer)
        else:
            self.save_text_answer(question, contact, answer)
        return HttpResponse(status=status.HTTP_200_OK)


@method_decorator(csrf_exempt, name='dispatch')
class GetTwilioSurveyEndpoint(APIView):
    def get(self, request):
        data = {
            'get_greetings': reverse('srm:api_marketing:api_surveys:twilio-get-greetings'),
            'get_question': reverse('srm:api_marketing:api_surveys:twilio-get-question'),
            'get_final_message': reverse('srm:api_marketing:api_surveys:twilio-get-final-message'),
            'submit_answer': reverse('srm:api_marketing:api_surveys:twilio-submit-answer')
        }
        return Response(data, status=status.HTTP_200_OK)
