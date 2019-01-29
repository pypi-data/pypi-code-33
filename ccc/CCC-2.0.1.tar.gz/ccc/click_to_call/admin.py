from django.contrib import admin

from ccc.click_to_call.models import (AssociateMasterList, AutoDialerList,
                                      CallHistory, PersonalizedMessage,
                                      RealPhoneValidation, TwimlApplication)


# Register your models here.
class AssociateMasterListAdmin(admin.ModelAdmin):
    list_display = ['name', "email", "user_name"]

    def email(self, obj):
        return obj.user.email

    def user_name(self, obj):
        return obj.user.full_name


class AutoDialerListAdmin(admin.ModelAdmin):
    list_display = ['phone_number', 'phone_friendly_number', "associated_to__name",
                    "associated_to__user__email", 'is_valid', 'msg_err', 'is_processed']

    def associated_to__name(self, obj):
        return obj.associated_to.name

    def associated_to__user__email(self, obj):
        return obj.associated_to.user.email


class CallHistoryAdmin(admin.ModelAdmin):
    list_display = ['number__number', "dialed_time",
                    "call_duration_in_seconds"]

    def number__number(self, obj):
        return obj.number.number


class RealPhoneValidationAdmin(admin.ModelAdmin):
    list_display = ['phone_number', 'phone_type', 'phone_status', 'phone_carrier', 'last_updated']


admin.site.register(AssociateMasterList, AssociateMasterListAdmin)
admin.site.register(AutoDialerList, AutoDialerListAdmin)
admin.site.register(CallHistory, CallHistoryAdmin)
admin.site.register(RealPhoneValidation, RealPhoneValidationAdmin)
admin.site.register(TwimlApplication)
admin.site.register(PersonalizedMessage)
