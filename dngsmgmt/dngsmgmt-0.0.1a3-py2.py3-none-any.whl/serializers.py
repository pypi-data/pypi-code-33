from . import models

from rest_framework import serializers


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Project
        exclude = ('permission',)


class ProjectMetadataSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ProjectMetadata
        fields = '__all__'


class ExperimentTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ExperimentType
        fields = '__all__'


class ExperimentSerializer(serializers.ModelSerializer):
    type = ExperimentTypeSerializer()
    project = ProjectSerializer()

    class Meta:
        model = models.Experiment
        exclude = ('permission',)


class ExperimentMetadataSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ExperimentMetadata
        fields = '__all__'


class SampleSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Sample
        exclude = ('permission',)


class SampleMetadataSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.SampleMetadata
        fields = '__all__'


class ConditionSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Condition
        exclude = ('permission',)


class ConditionMetadataSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ConditionMetadata
        fields = '__all__'
