import logging

from cloud_tools.contrib.mail.send import send_templated_email
from django.contrib.sites.models import Site
from django.template import Context, Template
from django.urls import reverse
from sorl.thumbnail import get_thumbnail

from ccc.campaigns.cloud_tasks import voice_call
from ccc.campaigns.models import (OMMS,  # TODO integrate this with Gcloud storage.
                                  OSMS, OEmail)
from ccc.template_design.models import CampaignTemplateDesign

logger = logging.getLogger(__name__)


def follow_up_campaign_send_sms(campaign, contact):
    """Follow up campaign send SMS"""
    twilio_number = campaign.campaign.phone.twilio_number
    # If campaign user have balance/credits
    if campaign.user.balance.get('sms', 0) > 0:
        text = Template(campaign.sms_text).render(Context(contact.template_context))

        OSMS.objects.create(from_no=twilio_number, text=text, fu_campaign=campaign, to=contact.phone, )
        return "Sent sms for campaign {} from {} to {}".format(campaign.name, twilio_number, contact.phone)

    return "Do not have balance for sms campaign {} from {} to {}".format(campaign.name, twilio_number, contact.phone)


def follow_up_campaign_send_mms(fu_campaign, contact):
    """Follow up campaign send MMS"""
    twilio_number = fu_campaign.parent_campaign.phone.twilio_number

    if fu_campaign.user.balance.get('mms', 0) > 0:
        media = []
        mms_campaign = fu_campaign.mmscampaign_set.last()
        if mms_campaign.image1:
            # TODO integrate this with Gcloud storage.
            thumbnail = get_thumbnail(mms_campaign.image1, '300x200', quality=99)
            media.append(thumbnail.url)

        if mms_campaign.image2:
            thumbnail = get_thumbnail(mms_campaign.image2, '300x200', quality=99)
            media.append(thumbnail.url)

        if mms_campaign.video:
            media.append(mms_campaign.video.url)

        OMMS.objects.create(from_no=twilio_number, to=contact.phone, campaign=fu_campaign,
                            text=mms_campaign.text, media=media)
        return "Sent mms for fu campaign {} from {} to {}".format(fu_campaign.name, twilio_number, contact.phone)
    return "Do not have balance for mms fu campaign {} from {} to {}".format(fu_campaign.name, twilio_number,
                                                                             contact.phone)


def is_srm_fusion_campaign(campaign):
    return campaign.emailcampaign_set.first()


def campaign_send_email(model, campaign, contact, is_srm_fusion=False):
    # TODO Awesome BAD code, this is legacy and pass also from the old version. #NeedRefactor
    hostname = Site.objects.first().domain
    logo = None
    email_context = {}
    body_context = {}
    body_context.update(contact.template_context)
    email_subject = ""
    attachments = []
    output_email_attributes = {}
    if not model == 'FUCampaign':
        if not campaign.use_email:
            return
        email_campaign = is_srm_fusion_campaign(campaign)
        if email_campaign:
            campaign.from_email = email_campaign.from_email
            email_subject = email_campaign.subject
            if email_campaign.email_type == 'premium':
                email_template = email_campaign.premium_template
                email_context['body'] = Template(email_template.email_body).render(Context(body_context))
                email_context.update(contact.template_context)
            else:
                email_body = Template(email_campaign.body).render(Context(body_context))
                body_context.update({'body': email_body, 'e_greeting': email_body})
                email_body = Template(email_campaign.template.email_body).render(Context(body_context))
                email_context['e_greeting'] = email_context['body'] = email_body

        elif campaign.email_type == 'premium':
            email_template = CampaignTemplateDesign.objects.get(campaign=campaign, template_type='email')
            email_context['body'] = email_template.template.email_body
            email_context.update(contact.template_context)
        elif campaign.e_greeting:
            email_context['body'] = Template(campaign.e_greeting).render(Context(body_context))

    if model == 'FUCampaign':
        logo = campaign.campaign.logo
        try:
            email_context['body'] = Template(campaign.email_body).render(Context(body_context))
            email_subject = campaign.email_subject
            email_context['e_greeting'] = Template(campaign.email_body).render(Context(body_context))
        except TypeError:
            email_obj = campaign.emailcampaign_set.first()
            if email_obj:
                body_context.update({'body': email_obj.body, 'e_greeting': email_obj.body})
                email_body = Template(email_obj.template.email_body).render(Context(body_context))
                email_context['e_greeting'] = email_context['body'] = email_body
                email_subject = email_obj.subject
        email_context['company'] = campaign.campaign.company
        email_context['name'] = campaign.name
        email_context['protocol'] = "https://"
        email_context['hostname'] = hostname
        email_context['username'] = contact.first_name
        email_context['analytic_data'] = {
            'sender_id': campaign.user.id,
            'last_name': contact.last_name,
            'first_name': contact.first_name,
            'contact_id': contact.id,
            'campaign_id': campaign.id,
            'campaign_name': campaign.name,
            'from_email': campaign.from_email,
            'to_email': contact.email,
            'type': 'email'
        }
        objects = list(campaign.templateimages_set.all()[:campaign.template.number_of_max_uploads])
        for l in range(campaign.template.number_of_max_uploads - len(objects)):
            objects.append({})

        email_context['objects'] = objects
        output_email_attributes = {'fu_campaign': campaign, 'campaign': campaign.campaign, }

    elif model == 'Campaign':
        logo = campaign.logo
        email_context['company'] = campaign.company
        email_context['name'] = campaign.name
        email_context['protocol'] = "https://"
        email_context['hostname'] = hostname
        email_context['username'] = contact.first_name
        email_context['analytic_data'] = {
            'sender_id': campaign.user.id,
            'last_name': contact.last_name,
            'first_name': contact.first_name,
            'contact_id': contact.id,
            'campaign_id': campaign.id,
            'campaign_name': campaign.name,
            'from_email': campaign.from_email,
            'to_email': contact.email,
            'type': 'email'

        }
        template_image = campaign.templateimages_set.all()
        if template_image:
            objects = list(
                campaign.templateimages_set.all()[:campaign.template.number_of_max_uploads])
            for l in range(campaign.template.number_of_max_uploads - len(objects)):
                objects.append({})
            email_context['objects'] = objects

        output_email_attributes = {
            'campaign': campaign,
        }

    if logo:
        try:
            email_context['logo'] = "https://{}{}".format(hostname, logo.url)
        except BaseException:
            email_context['logo'] = logo.path

        try:
            output_email_attributes['logo'] = logo.path
        except BaseException:
            output_email_attributes['logo'] = ''

    if contact.first_name:
        email_context["contact_fname"] = contact.first_name
        output_email_attributes['lead_name'] = contact.first_name
    if contact.last_name:
        output_email_attributes['last_name'] = contact.last_name

    if campaign.user.balance.get('email', 0) > 0 and email_context.get('body'):
        logger.info("Sending email to: {} {}".format(contact.email, hostname))
        send_templated_email(
            subject=email_subject, email_body=email_context['body'], sender=campaign.from_email,
            recipients=contact.email, email_context=email_context, files=attachments
        )
        output_email_attributes.update({
            'from_email': campaign.from_email,
            'to_email': contact.email,
            'body': email_context['body'],
            'subject': email_subject,
            'company': email_context['company'],
            'user': campaign.user,
            'sent': True
        })
        OEmail.objects.create(**output_email_attributes)

    return "Sending email to: {} {}".format(contact.email, hostname)


def follow_up_campaign_send_email(campaign, contact):
    campaign_send_email('FUCampaign', campaign, contact)


def follow_campaign_make_call(fu_campaign, contact):
    """Follow Campaigns. Make a Call"""

    hostname = Site.objects.first().domain
    relative_url = reverse('srm:api_marketing:campaigns:make-call', kwargs={'pk': fu_campaign.id})

    url = 'https://%s%s' % (hostname, relative_url)
    if fu_campaign.user.balance.get('talktime', 0) > 0:
        # Do a call, this is send to the voice-calls queue
        voice_call(url=url, to_phone=contact.phone,
                   from_phone=fu_campaign.parent_campaign.phone.twilio_number).execute()
