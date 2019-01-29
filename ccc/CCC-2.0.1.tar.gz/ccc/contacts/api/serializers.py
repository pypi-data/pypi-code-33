import django_filters
from django.db import transaction
from django_filters.rest_framework import FilterSet
from rest_framework import serializers

from ccc.campaigns.models import Campaign
from ccc.contacts.models import (CompanySocialProfile, Contact, ContactGroup,
                                 ContactNote, ContactSocialProfile)
from ccc.marketing.campaigns.api.serializers import CampaignSerializer


class ContactSocialProfileFilter(FilterSet):
    class Meta:
        model = ContactSocialProfile
        exclude = ('dataAddOns', 'details', 'data')


class ContactSocialProfileSerializer(serializers.ModelSerializer):
    """Contact Social profile serializer"""

    class Meta(object):
        model = ContactSocialProfile
        fields = '__all__'


class CompanySocialProfileFilter(FilterSet):
    class Meta:
        model = CompanySocialProfile
        exclude = ('dataAddOns', 'details', 'data')


class CompanySocialProfileSerializer(serializers.ModelSerializer):
    """Company Social profile serializer"""

    class Meta(object):
        model = CompanySocialProfile
        fields = '__all__'


class ContactFilter(FilterSet):
    start_date = django_filters.IsoDateTimeFilter(name='created_at', lookup_expr='gte')
    end_date = django_filters.IsoDateTimeFilter(name='created_at', lookup_expr='lte')
    first_name = django_filters.CharFilter(name='first_name', lookup_expr='icontains')
    last_name = django_filters.CharFilter(name='last_name', lookup_expr='icontains')
    campaign = django_filters.CharFilter(name='campaigns__pk')
    phone = django_filters.CharFilter(name='last_name', lookup_expr='icontains')
    cell_number = django_filters.CharFilter(name='last_name', lookup_expr='icontains')

    class Meta:
        model = Contact
        exclude = ('card_image', 'card_front_image', 'card_back_image', 'profile_image')


class ContactGroupSerializer(serializers.ModelSerializer):
    """Contact Group Serializer"""

    class Meta:
        model = ContactGroup
        fields = '__all__'


class ContactSerializer(serializers.ModelSerializer):
    """Contact Serializer"""
    groups = serializers.PrimaryKeyRelatedField(many=True, queryset=ContactGroup.objects.all(), read_only=False,
                                                write_only=False)
    campaign_objects = CampaignSerializer(read_only=True, source='campaigns', many=True)
    group_objects = ContactGroupSerializer(read_only=True, source='groups', many=True)
    social = serializers.SerializerMethodField()

    class Meta:
        model = Contact
        fields = '__all__'
        extra_kwargs = {
            'campaigns': {
                'allow_empty': True
            },
            'groups': {
                'allow_empty': True
            }
        }

    def get_social(self, obj):
        soc_profile_obj = obj.social_profiles.first()
        if soc_profile_obj:
            return ContactSocialProfileSerializer(instance=soc_profile_obj).data
        return []

    def validate(self, attrs):
        #  Validate Phone
        phone = attrs.get('phone', None)
        email = attrs.get('email', None)
        user = self.context['request'].user
        #  If update
        instance_id = self.instance.id if self.instance else None
        errors = dict()
        queryset = Contact.objects.filter(user=user)
        if not attrs.get('contact_type') == 'DBC':
            if queryset.filter(phone=phone).exclude(pk=instance_id).exists():
                errors.update({'phone': ['This phone number already exists in your contacts!']})
            if queryset.filter(email=email).exclude(pk=instance_id).exists():
                errors.update({'email': ['This email already exists in your contacts!']})
        if errors:
            raise serializers.ValidationError(errors)
        return super(ContactSerializer, self).validate(attrs)

    @transaction.non_atomic_requests
    def create(self, validated_data):
        groups = validated_data.pop('groups')
        campaigns = validated_data.pop('campaigns')
        social_fields = [f.name for f in ContactSocialProfile._meta.get_fields()]
        social = {}
        request_data = self.context['request'].data
        for field in social_fields:
            if request_data.get(field):
                social[field] = request_data[field]
        contact = Contact.objects.create(**validated_data)
        if campaigns:
            contact.campaigns.add(*campaigns)
            contact.save()
        if groups:
            for group in groups:
                group.contacts.add(contact)
                group.save()
        if social:
            ContactSocialProfile.objects.create(contact=contact, **social)
        return contact


class ContactGroupFilter(FilterSet):
    class Meta:
        model = ContactGroup
        exclude = ('card_front_image', 'card_back_image',)


class ImportContactSerializer(serializers.Serializer):
    campaigns = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Campaign.objects.all(), read_only=False,
        write_only=False, required=False
    )
    groups = serializers.PrimaryKeyRelatedField(
        many=True, queryset=ContactGroup.objects.all(), read_only=False,
        write_only=False, required=False
    )


class UploadContactSerializer(ImportContactSerializer):
    excel = serializers.FileField()


class ValidateContactUploadSerializer(UploadContactSerializer):
    drop_first_row = serializers.CharField(required=False)


class ContactNoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactNote
        fields = '__all__'
        extra_kwargs = {
            'contact': {
                'required': False,
                'allow_null': True
            }
        }
