from rest_framework import serializers

from ccc.survey.models import Survey, SurveyMappedKeywords


class SurveyKeywordSerializer(serializers.ModelSerializer):
    mapped_keywords = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()
    phone_number = serializers.SerializerMethodField()
    initity_id = serializers.SerializerMethodField()

    class Meta:
        model = Survey
        fields = ['mapped_keywords', 'name', 'phone_number', 'initity_id']

    def get_phone_number(self, obj):
        return obj.phone

    def get_initity_id(self, obj):
        return obj.id

    def get_name(self, obj):
        return obj.title

    def get_mapped_keywords(self, obj):
        mapped_keywords = SurveyMappedKeywords.objects.filter(
            survey=obj.id,
            is_active=True).values_list('keyword', flat=True)
        mapped_keywords = ", ".join([str(x) for x in mapped_keywords])
        return mapped_keywords


class SurveyAppSerializer(serializers.ModelSerializer):

    """
    Purpose: A serializer that deals with Details instances and
    querysets.
    """

    class Meta(object):
        model = Survey
        fields = '__all__'
