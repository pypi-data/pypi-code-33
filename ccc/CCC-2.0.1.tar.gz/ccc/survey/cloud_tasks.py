import logging

from django.conf import settings
from gcloud_tasks.decorators import task
from twilio.base.exceptions import TwilioException
from twilio.rest import Client

from ccc.campaigns.utils.shortcut import audio_conversion
from ccc.contacts.models import Contact
from ccc.survey.models import Question, Survey

logger = logging.getLogger(__name__)


@task(queue=settings.GOOGLE_TASK_QUEUE_DEFAULT)
def survey_convert_audio_format(request, survey_id):
    try:
        survey = Survey.objects.get(pk=survey_id)
    except Survey.DoesNotExist:
        logging.info("Invalid survey id: {}".format(survey_id))
        return
    if not survey.voice_greeting:
        logging.info("No voice file found. Survey id: {}".format(survey.id))
        return

    voice_greeting = survey.voice_greeting_original

    voice_greeting_converted = audio_conversion(voice_greeting)

    survey.voice_greeting_converted = voice_greeting_converted
    survey.save()
    logging.info("Voice converted successfully. Survey id {}".format(survey.id))


@task(queue=settings.GOOGLE_TASK_QUEUE_DEFAULT)
def trigger_survey(request, survey_id, contact_ids):
    try:
        survey = Survey.objects.get(pk=survey_id)
        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        contacts = Contact.objects.filter(pk__in=contact_ids, phone__isnull=False)
        for contact in contacts:
            # Check if the contact still has pending questions
            if Question.objects.question_for_contact(survey, contact):
                logging.error('Triggering Survey {} to: {}'.format(survey_id, contact.phone.as_international))
                client.studio.flows(settings.TWILIO_SURVEY_FLOW_ID).executions.create(to=contact.phone.as_international,
                                                                                      from_=survey.phone.twilio_number)
    except TwilioException as e:
        logging.error('Error triggering Survey {} : {}'.format(survey_id, e))
    return
