from rest_framework import serializers

from ccc.contacts.models import (CompanySocialProfile, Contact, ContactGroup,
                                 ContactSocialProfile)


class ContactSerializer(serializers.ModelSerializer):

    class Meta:
        model = Contact
        exclude = ('note', 'call_sid', 'sms_sid', 'survey', 'lead_type')

    def get_fields(self, *args, **kwargs):
        fields = super(ContactSerializer, self).get_fields(*args, **kwargs)
        request = self.context.get('request', None)
        if request:
            try:
                fields['campaigns'].queryset = fields['campaigns'].queryset.filter(
                    user=request.user,
                    active=True)
            except Exception as ex:
                # Swagger Fix
                pass
            # TODO: Fix: Validtion is not working this way
            fields['campaigns'].required = True
        fields['card_image'].required = True
        return fields

    def validate(self, attrs):
        if not attrs.get('campaigns', None):
            raise serializers.ValidationError(
                "campaigns: This field is required")
        return super(ContactSerializer, self).validate(attrs)


class ContactSocialProfileSerializer(serializers.ModelSerializer):
    """Contact Social profile serializer"""
    class Meta(object):
        model = ContactSocialProfile
        fields = ('id', 'website', 'bio', 'title', 'gender', 'twitter', 'linkedin', 'facebook', 'location',
                  'organization', 'avatar')


class CompanySocialProfileSerializer(serializers.ModelSerializer):
    """Company Social profile serializer"""
    class Meta(object):
        model = CompanySocialProfile
        fields = ('id', 'website', 'bio', 'name', 'founded', 'twitter', 'linkedin', 'facebook', 'location',
                  'locale', 'logo', 'category', 'employees')


class ContactListSerializer(serializers.ModelSerializer):

    """
    Purpose: A serializer that deals with Details instances and
    querysets.
    """
    campaigns_ids = serializers.SerializerMethodField()
    campaigns_names = serializers.SerializerMethodField()
    surveys_names = serializers.SerializerMethodField()
    social_profiles = serializers.SerializerMethodField()
    company_profiles = serializers.SerializerMethodField()
    groups_ids = serializers.SerializerMethodField()
    groups_names = serializers.SerializerMethodField()
    checkins_names = serializers.SerializerMethodField()

    def get_campaigns_ids(self, obj):
        return obj.campaigns.all().values_list('id', flat=True)

    def get_campaigns_names(self, obj):
        return obj.campaigns.all().values_list('name', flat=True)

    def get_surveys_names(self, obj):
        return [obj.survey.title] if obj.survey else []

    def get_groups_ids(self, obj):
        return obj.groups.all().values_list('id', flat=True)

    def get_groups_names(self, obj):
        return obj.groups.all().values_list('name', flat=True)

    def get_checkins_names(self, obj):
        return obj.checkins.all().values_list('campaign__name', flat=True)

    def get_social_profiles(self, obj):
        """Get social profile for contact"""
        soc_profile_obj = obj.social_profiles.first()
        if soc_profile_obj:
            return ContactSocialProfileSerializer(instance=soc_profile_obj).data

    def get_company_profiles(self, obj):
        """Get Company profile for contact"""
        soc_profile_obj = obj.company_social_profiles.first()
        if soc_profile_obj:
            return ContactSocialProfileSerializer(instance=soc_profile_obj).data

    class Meta(object):
        model = Contact
        fields = ('id', 'first_name', 'last_name',
                  'email', "phone", "created_at", "card_image", "card_front_image",
                  "card_back_image", "campaigns_ids", "campaigns_names", "surveys_names",
                  "groups_ids", "groups_names", "note",
                  "checkins_names", "company_name",
                  "country", "social_profiles", "company_profiles")


class LimitedContactListSerializer(serializers.ModelSerializer):

    """
    Purpose: A serializer that deals with Details instances and
    querysets.
    """
    class Meta(object):
        model = Contact
        fields = ('id', 'first_name', 'last_name',
                  'email', "phone", "company_name",
                  "country")


class ContactGroupListSerializer(serializers.ModelSerializer):

    """
    Purpose: A serializer that deals with Details instances and
    querysets.
    """

    class Meta(object):
        model = ContactGroup
        fields = ('id', 'name',)
