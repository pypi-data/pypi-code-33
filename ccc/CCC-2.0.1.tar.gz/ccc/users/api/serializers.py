from rest_framework import serializers

from ccc.users.models import UserProfile

EXCLUDE_FIELDS = (
    'activation_key',
    'address',
    'city',
    'company_name',
    'country',
    'groups',
    'industry',
    'interface_language',
    'is_accepted_term',
    'is_admin',
    'is_buyer',
    'is_notification_enabled',
    'is_phone_verified',
    'is_staff',
    'is_superuser',
    'is_supplier',
    'is_tenant',
    'last_login',
    'next_payment_attempt',
    'password',
    'payment_failed',
    'privacy_settings',
    'security_question',
    'security_answer',
    'tutorial_shown',
    'user_code',
    'user_permissions'
)


class UserModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        extra_kwargs = {
            'first_name': {
                'allow_null': False,
                'allow_blank': False
            },
            'last_name': {
                'allow_null': False,
                'allow_blank': False
            },
            'email': {
                'allow_null': False,
                'allow_blank': False
            }
        }
        exclude = EXCLUDE_FIELDS


class AddSubUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        exclude = EXCLUDE_FIELDS
        extra_kwargs = {
            'first_name': {
                'allow_null': False,
                'allow_blank': False
            },
            'last_name': {
                'allow_null': False,
                'allow_blank': False
            },
            'email': {
                'allow_null': False,
                'allow_blank': False
            },
            'password': {
                'allow_blank': True,
                'allow_null': True,
                'required': False
            }
        }


class ViewSubUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        exclude = EXCLUDE_FIELDS
