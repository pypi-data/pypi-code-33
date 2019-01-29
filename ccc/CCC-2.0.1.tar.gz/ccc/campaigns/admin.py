from adminsortable.admin import SortableAdmin
from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin

from ccc.campaigns.models import (IMMS, ISMS, OMMS, OSMS, Campaign,
                                  CampaignEmailTemplate, EmailCampaign,
                                  IEmail, IVoiceCall,
                                  MappedKeywords, MMSCampaign, Notify, OEmail,
                                  OVoiceCall, RedirectNumber, RejectedNumber,
                                  SampleVoiceCall, SMSCampaign, TemplateImages,
                                  TemplateType, VoiceCampaign, FollowUpDetail)


class OSMSAdmin(admin.ModelAdmin):
    list_display = ['to', 'from_no', 'text', 'num_segments', 'status',
                    'date_created', 'last_updated', 'send_at', 'countdown', 'sent']
    search_fields = ['to', 'from_no', 'text', 'message_sid']
    list_filter = ['status', 'sent', 'is_sample']


class FUAdmin(admin.ModelAdmin):
    list_display = ['name', 'campaign', 'duration', 'send_at',
                    'custom', 'specific', 'recur', 'onleadcapture', 'now4leads']


class IVAdmin(admin.ModelAdmin):
    list_display = ['from_no', 'to', 'date_created',
                    'status', 'last_updated', 'completed', 'charged']
    search_fields = ['from_no', 'to', 'call_sid']
    list_filter = ['status', 'completed', 'charged']


class OVAdmin(admin.ModelAdmin):
    list_display = [
        'from_no', 'to', 'date_created', 'status', 'last_updated', 'charged']
    search_fields = ['from_no', 'to', 'call_sid']
    list_filter = ['status', 'charged']


class CampaignEmailTemplateAdmin(SortableAdmin):
    list_display = ['name', 'template_type', 'number_of_max_uploads',
                    'private_template', 'date_created', 'last_updated']
    list_filter = ['private_template', 'number_of_max_uploads']


class RedirectNumberAdmin(admin.ModelAdmin):
    list_display = ('user', 'from_no', 'to_no', 'code', 'date_created',
                    'last_updated', 'verified')


class OEmailAdmin(admin.ModelAdmin):
    list_display = ['from_email', 'to_email', 'user',
                    'time', 'campaign', 'send_at', 'sent']
    search_fields = ['from_email', 'to_email',
                     'user__email', 'campaign__name', 'subject']
    list_filter = ['sent', ]


class OMMSAdmin(admin.ModelAdmin):
    list_display = ['to', 'from_no', 'text', 'status',
                    'date_created', 'last_updated', 'countdown']
    search_fields = ['to', 'from_no', 'text', 'message_sid']
    list_filter = ['status', 'is_sample']


class MappedKeywordsAdmin(admin.ModelAdmin):
    list_display = ['keyword', "campaign"]


class RejectedNumberAdmin(admin.ModelAdmin):
    list_display = ['reject_number', 'reject_for_all', "on_twilio_number"]

    def on_twilio_number(self, obj):
        if obj.reject_for_all:
            return "ALL"
        number_list = []
        numbers = obj.twilio_numbers.all()
        for no in numbers:
            number_list.append(no.twilio_number)
        return number_list


class CampaignHistoryAdmin(SimpleHistoryAdmin):
    list_display = (
    'id', 'name', 'phone',  'from_email', 'use_email', 'use_voice', 'use_sms', 'user', 'active', 'created_at', 'start_at')
    history_list_display = ["status"]
    ordering = ['-active', '-created_at']
    search_fields = ['name']


class FollowUpCampaignHistoryAdmin(SimpleHistoryAdmin):
    list_display = ('campaign', 'sent', 'sp_date', 'sp_date_tz', 'date_created', 'last_updated')
    history_list_display = ["status"]


admin.site.register(CampaignEmailTemplate, CampaignEmailTemplateAdmin)
admin.site.register(VoiceCampaign)
admin.site.register(EmailCampaign)
admin.site.register(SMSCampaign)
admin.site.register(SampleVoiceCall)
admin.site.register(IVoiceCall, IVAdmin)
admin.site.register(ISMS)
admin.site.register(IEmail)
admin.site.register(OEmail, OEmailAdmin)
admin.site.register(IMMS)
admin.site.register(OMMS, OMMSAdmin)
admin.site.register(OSMS, OSMSAdmin)

admin.site.register(OVoiceCall, OVAdmin)
admin.site.register(MMSCampaign)
admin.site.register(RedirectNumber, RedirectNumberAdmin)
admin.site.register(Notify)
admin.site.register(TemplateType)

admin.site.register(TemplateImages)
admin.site.register(MappedKeywords, MappedKeywordsAdmin)
admin.site.register(RejectedNumber, RejectedNumberAdmin)

admin.site.register(Campaign, CampaignHistoryAdmin)
admin.site.register(FollowUpDetail, FollowUpCampaignHistoryAdmin)
