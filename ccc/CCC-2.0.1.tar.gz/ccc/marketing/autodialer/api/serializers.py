from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from ccc.click_to_call.models import AutoDialerList, PersonalizedMessage


class AutoDialerSerializer(serializers.ModelSerializer):
    class Meta:
        model = AutoDialerList
        fields = '__all__'


def validate_voice_file_size(file):
    # Ensure that file is not larger than 64kb
    if file.size > 64000:
        raise serializers.ValidationError('File size of {}kb exceeds limit of 64kb, you might want to record a '
                                          'shorter audio or upload a less heavier file'.format(file.size / 1000))


class PersonalizedMessageSerializer(serializers.ModelSerializer):
    audio = serializers.FileField(validators=[validate_voice_file_size], required=False)
    name = serializers.CharField(max_length=255, validators=[UniqueValidator(queryset=
                                                                             PersonalizedMessage.objects.all())])

    class Meta:
        model = PersonalizedMessage
        fields = '__all__'
        extra_kwargs = {
            'user': {
                'required': False
            },
            'text': {
                'required': False,
                'allow_blank': True
            },
            'audio': {
                'required': False,
                'allow_null': True
            }
        }

    def validate(self, attrs):
        super(PersonalizedMessageSerializer, self).validate(attrs)
        text = attrs.get('text')
        type_ = attrs.get('type')
        audio = attrs.get('audio')
        if type_ == 'voice':
            if not audio and not text:
                raise serializers.ValidationError('You need to add either an audio file or some text')
        elif type_ == 'sms':
            if not text:
                raise serializers.ValidationError('You need to add text for SMS type')
        return attrs


class SendPersonalizedMessageSerializer(serializers.Serializer):
    contacts = serializers.ListField(allow_empty=False)
    from_ = serializers.CharField(required=True)
