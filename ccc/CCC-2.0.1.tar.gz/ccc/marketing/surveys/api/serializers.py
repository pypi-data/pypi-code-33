""""
Serializers for Survey's API.
"""
from django.urls import reverse
from rest_framework import serializers

from ccc.contacts.api.serializers import ContactSerializer
from ccc.marketing.api.serializers import TwilioNumberSerializer
from ccc.packages.models import TwilioNumber
from ccc.survey.models import (AnswerChoice, Question, Survey,
                               SurveyMappedKeywords, UserAnswer)
from django_filters import rest_framework as django_filters
from django_filters.rest_framework import FilterSet


class SurveyFilter(FilterSet):
    title = django_filters.CharFilter(name='title', lookup_expr='icontains')
    created = django_filters.DateFilter(lookup_expr='icontains', name='created')

    class Meta:
        model = Survey
        exclude = ('voice_greeting_original', 'voice_greeting_converted',)


class SurveySerializer(serializers.ModelSerializer):
    """Listing surveys."""
    phone = TwilioNumberSerializer(read_only=True)

    phone_id = serializers.PrimaryKeyRelatedField(
        queryset=TwilioNumber.objects.all(),
        source='phone',
        required=True
    )

    survey_details_url = serializers.SerializerMethodField(read_only=True)
    survey_archived_url = serializers.SerializerMethodField(read_only=True)
    survey_un_archived_url = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Survey
        fields = (
            'id', 'phone', 'active', 'phone_id', 'created', 'title', 'survey_details_url', 'survey_archived_url',
            'greeting_text', 'last_message', 'campaign', 'voice_greeting_original', 'survey_un_archived_url'
        )
        extra_kwargs = {
            'campaign': {
                'required': False
            },
            'voice_greeting_original': {
                'required': False,
                'allow_null': True
            },
            'greeting_text': {
                'required': False,
                'allow_blank': True,
                'allow_null': True
            }
        }

    def get_survey_archived_url(self, obj):
        """Reverse survey URL for archived"""
        if obj:
            url = reverse('srm:api_marketing:api_surveys:surveys-archived', args=[obj.id])
            return url

    def get_survey_un_archived_url(self, obj):
        """Reverse survey URL for archived"""
        if obj:
            url = reverse('srm:api_marketing:api_surveys:surveys-unarchived', args=[obj.id])
            return url

    def get_survey_details_url(self, obj):
        """Reverse survey detail URL'S"""
        return reverse('srm:marketing:surveys:survey_detail', args=[obj.id])

    def validate(self, data):
        greeting_was_uploaded = data.get('voice_greeting_original') or data.get('greeting_text')
        greeting_already_exists = self.instance and (self.instance.voice_greeting_original or
                                                     self.instance.greeting_text)
        if not greeting_was_uploaded and not greeting_already_exists:
            raise serializers.ValidationError({'voice_greeting_original': 'Please provide audio or greetings text',
                                               'greeting_text': 'Please provide audio or greetings text'})
        return super(SurveySerializer, self).validate(data)

    def create(self, validated_data):
        request = self.context.get("request")
        validated_data['user'] = request.user
        validated_data['active'] = True
        return self.Meta.model.objects.create(**validated_data)


class RecursiveField(serializers.Serializer):
    def to_representation(self, value):
        serializer = self.parent.parent.__class__(value, context=self.context)
        return serializer.data


class AnswerChoiceSerializer(serializers.ModelSerializer):
    """Serializer for AnswersChoice Questions"""
    id = serializers.IntegerField(required=False)  # we add this field to enable us edit its instance from question

    class Meta:
        model = AnswerChoice
        fields = (
            'id',
            'answer',
            'should_halt'
        )


class QuestionFilter(FilterSet):
    class Meta:
        model = Question
        exclude = ('voice_greeting_original', 'voice_greeting_converted',)


class QuestionSerializer(serializers.ModelSerializer):
    """Serializer for survey questions"""
    survey = SurveySerializer(read_only=True)
    survey_id = serializers.PrimaryKeyRelatedField(queryset=Survey.objects.all(), write_only=True, source='survey')
    in_response_of = AnswerChoiceSerializer(many=True, allow_null=True, read_only=True)
    in_response_of_question = RecursiveField(many=True, allow_null=True, read_only=True)
    answer_choices = AnswerChoiceSerializer(many=True, allow_null=True)
    question_type_name = serializers.SerializerMethodField(read_only=True)
    schedular_step = serializers.SerializerMethodField(read_only=True)
    parent_question = serializers.PrimaryKeyRelatedField(write_only=True, queryset=Question.objects.all(),
                                                         required=False, allow_null=True)
    parent_answer = serializers.PrimaryKeyRelatedField(write_only=True, queryset=AnswerChoice.objects.all(),
                                                       required=False, allow_null=True)
    has_children = serializers.SerializerMethodField()

    class Meta:
        model = Question
        fields = (
            'id', 'delay', 'survey', 'survey_id', 'question', 'question_type', 'contact_mapping',
            'in_response_of_question', 'in_response_of', 'question_type_name', 'schedular_step', 'delay_value',
            'answer_choices', 'parent_question', 'parent_answer', 'has_children'
        )

        read_only_fields = ('id', 'survey', 'question_type_name', 'in_response_of_question')

    def get_schedular_step(self, obj):
        """Custom field. Read only. Returns schedular_step information"""
        return obj.schedular_step

    def get_delay_value(self, obj):
        """Custom field. Read only. Returns delay value converted from the seconds to the original value choosed"""
        return obj.delay_value

    def get_question_type_name(self, obj):
        """Returns question type"""
        return self.Meta.model.TYPES[obj.question_type]

    def get_has_children(self, obj):
        """We are checking if the survey question has follow up questions to itself or its options"""
        answer_choices = obj.answer_choices.all().values_list('id', flat=True)
        has_questions_to_options = self.Meta.model.objects.filter(in_response_of__in=answer_choices).exists()
        return obj.next_questions.exists() or has_questions_to_options

    def validate(self, attrs):
        options = attrs.get('answer_choices')
        question_type = attrs.get('question_type')
        if question_type == 'mcq' and len(options) < 2:
            raise serializers.ValidationError(
                {'question_type': 'You need to provide at least two options for a Multiple '
                                  'choice question'})
        return super(QuestionSerializer, self).validate(attrs)

    def create(self, validated_data):
        parent_question = validated_data.pop('parent_question', None)
        answer_choices = validated_data.pop('answer_choices')
        parent_answer = validated_data.pop('parent_answer', None)
        question = self.Meta.model.objects.create(**validated_data)
        answers_models = list()
        for index, answer in enumerate(answer_choices):
            answers_models.append(AnswerChoice(**answer, code=index, question=question))
        AnswerChoice.objects.bulk_create(answers_models)
        if parent_answer:
            question.in_response_of.add(parent_answer)
        if parent_question:
            question.in_response_of_question.add(parent_question)
        return question

    def update(self, instance, validated_data):
        answer_choices = validated_data.pop('answer_choices')
        for key, value in validated_data.items():
            setattr(instance, key, value)
            instance.save()
        for index, item in enumerate(answer_choices):
            try:
                AnswerChoice.objects.get(pk=item.get('id'))
            except AnswerChoice.DoesNotExist:
                AnswerChoice.objects.create(**item, question=instance)
            else:
                AnswerChoice.objects.filter(pk=item.get('id')).update(**item, question=instance)
        return instance


class AnswerChoiceTreeViewSerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()

    class Meta:
        model = AnswerChoice
        fields = (
            'id', 'answer', 'children', 'should_halt'
        )

    def get_children(self, obj):
        return QuestionTreeViewSerializer(Question.objects.filter(in_response_of=obj).order_by('order'), many=True).data


class QuestionTreeViewSerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()
    answer_choices = AnswerChoiceTreeViewSerializer(many=True)
    schedular_step = serializers.CharField(read_only=True)
    delay_value = serializers.CharField(read_only=True)

    class Meta:
        model = Question
        fields = (
            'id', 'survey_id', 'question', 'question_type', 'in_response_of_question', 'in_response_of',
            'answer_choices', 'children', 'delay_value', 'schedular_step'
        )

    def get_children(self, obj):
        return QuestionTreeViewSerializer(obj.next_questions.all().order_by('order'), many=True).data


class MappedKeywordSerializer(serializers.ModelSerializer):
    keywords = serializers.ListField(write_only=True)

    class Meta:
        model = SurveyMappedKeywords
        fields = '__all__'

    def validate(self, attrs):
        keywords = attrs.get("keywords", [])
        if not keywords:
            raise serializers.ValidationError({'keywords': 'Enter at least one keyword!'})

        survey = attrs.get('survey')
        used_instances = SurveyMappedKeywords.objects.filter(keyword__in=keywords, survey__phone=survey.phone)

        if used_instances.exists():
            used_ones = used_instances.values_list('keyword', flat=True)
            raise serializers.ValidationError({'keywords': str(list(used_ones)) + ' have been used already!'})
        return attrs

    def create(self, validated_data):
        survey = validated_data.get("survey")
        keywords = validated_data.get("keywords")
        SurveyMappedKeywords.objects.filter(
            survey=survey).update(is_active=False)
        key_obj = None
        for keyword in keywords:
            key_obj, created = SurveyMappedKeywords.objects.get_or_create(
                survey=survey,
                keyword=keyword)
            key_obj.is_active = True
            key_obj.save()
        # Return the last one
        return key_obj


class SurveyKeywordsSerializer(serializers.Serializer):
    survey = serializers.SerializerMethodField()
    keywords = serializers.SerializerMethodField()

    def get_survey(self, obj):
        return SurveySerializer(obj, context=self.context).data

    def get_keywords(self, obj):
        return MappedKeywordSerializer(obj.surveymappedkeywords_set.all(), many=True).data

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass


class UserAnswerSerializer(serializers.ModelSerializer):
    question = QuestionSerializer()
    contact = ContactSerializer()

    class Meta:
        model = UserAnswer
        fields = '__all__'


class TriggerSurveySerializer(serializers.Serializer):
    contacts = serializers.ListField()
    groups = serializers.ListField()
    survey_id = serializers.PrimaryKeyRelatedField(queryset=Survey.objects.all())

    def validate(self, attrs):
        if not attrs.get('contacts', []) and not attrs.get('groups', []):
            raise serializers.ValidationError('Please provide either a group(s) or contact(s)')
        return attrs


class ResortSurveyQuestionsSerializer(serializers.Serializer):
    parent_answer = serializers.IntegerField(required=False)
    parent_question = serializers.IntegerField(required=False)
    order = serializers.ListField(required=True)
