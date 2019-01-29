from ccc.campaigns.models import Campaign
from ccc.packages.models import TwilioNumber
from ccc.survey.models import Survey


def get_phone_number(user, campaign=None, survey=None):
    campaign_phones_ids = Campaign.objects.filter(phone__isnull=False).values_list('phone', flat=True)
    survey_phones_ids = Survey.objects.filter(phone__isnull=False).values_list('phone', flat=True)
    if campaign:
        campaign_phones_ids = campaign_phones_ids.exclude(id=campaign.id)
    if survey:
        survey_phones_ids = survey_phones_ids.exclude(id=survey.id)
    return TwilioNumber.objects.filter(user=user, is_redirected=False) \
        .exclude(id__in=campaign_phones_ids).exclude(id__in=survey_phones_ids)
