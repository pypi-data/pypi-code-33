from . import models

from rest_framework import serializers


class ComputationalToolCWLImportSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ComputationalToolCWLImport
        fields = '__all__'


class ComputationalToolInputTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ComputationalToolInputType
        fields = '__all__'


class ComputationalToolInputSerializer(serializers.ModelSerializer):
    computationaltoolinputtype = ComputationalToolInputTypeSerializer()

    class Meta:
        model = models.ComputationalToolInput
        exclude = ('computationaltool',)


class ComputationalToolSerializer(serializers.ModelSerializer):
    imports = ComputationalToolCWLImportSerializer(source="computationaltoolcwlimport_set",
                                                   many=True, read_only=True)
    inputs = ComputationalToolInputSerializer(source="computationaltoolinput_set",
                                              many=True, read_only=True)

    class Meta:
        model = models.ComputationalTool
        fields = '__all__'


class ComputationalToolSimplifiedSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ComputationalTool
        fields = '__all__'


class ComputationalWFCWLImportSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ComputationalWFCWLImport
        exclude = ('computationalwf',)


class ComputationalWFStepInputSerializer(serializers.ModelSerializer):
    computationaltoolinput = ComputationalToolInputSerializer()

    class Meta:
        model = models.ComputationalWFStepInput
        exclude = ('computationalwfstep',)


class ComputationalWFSerializerAsStep(serializers.ModelSerializer):
    inputs = ComputationalWFCWLImportSerializer(
        source="computationalwfcwlimport_set",
        many=True, read_only=True)

    class Meta:
        model = models.ComputationalWF
        fields = '__all__'


class ComputationalWFStepSerializer(serializers.ModelSerializer):
    inputs = ComputationalWFStepInputSerializer(
        source="computationalwfstepinput_set",
        many=True, read_only=True)
    computationaltool = ComputationalToolSimplifiedSerializer()
    computationalwfsteplist = ComputationalWFSerializerAsStep(
        source="computationalwfstep",
        read_only=True)

    class Meta:
        model = models.ComputationalWFStep
        exclude = ('computationalwf',)


class ComputationalWFSerializer(serializers.ModelSerializer):
    inputs = ComputationalWFCWLImportSerializer(
        source="computationalwfcwlimport_set",
        many=True, read_only=True)
    steps = ComputationalWFStepSerializer(source="computationalwf",
                                          many=True, read_only=True)

    class Meta:
        model = models.ComputationalWF
        fields = '__all__'
