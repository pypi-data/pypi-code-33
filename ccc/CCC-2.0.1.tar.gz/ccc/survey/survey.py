# coding: utf-8
import logging

from ccc.campaigns.models import OSMS
from ccc.contacts.models import Contact
from ccc.utils.utils import validate_media_absolute_url

from .models import Survey

logger = logging.getLogger(__name__)


class PhoneSurvey(object):
    """Wrap and utility survey obj"""

    def __init__(self, twilio_phone):
        self.twilio_number = twilio_phone.number
        self.obj = Survey.objects.filter(phone__twilio_number=self.twilio_number).first()

    @property
    def user(self):
        return self.obj.user

    @property
    def voice_greeting(self):
        return self.obj.voice_greeting

    @property
    def last_message(self):
        return self.obj.last_message

    @property
    def voice_greeting_url(self):
        return validate_media_absolute_url(self.obj.voice_greeting.url)

    @property
    def greeting_text(self):
        return self.obj.greeting_text

    def get_next_question(self, contact):
        """Return the current/next question of this survey and contact"""
        return self.obj.questions.question_for_contact(self.obj, contact)

    def add_campaign(self, contact):
        """Add survey campaign (if survey has) to the contact campaign"""
        if self.obj.campaign:
            contact.campaigns.add(self.obj.campaign)

    def send_sms(self, contact, to_number):
        """Returns true if OSMS was created"""
        next_question = self.get_next_question(contact)
        user_balance = self.obj.user.balance.get('sms', 0)

        if next_question and user_balance > 0:
            logger.info("SMS {} to {} . Delay secs:{}".format(self.twilio_number, to_number, next_question.delay))
            kwargs = {
                'from_no': self.twilio_number,
                'to': to_number,
                'text': next_question.get_message(contact),
                'countdown': next_question.delay
            }
            OSMS.objects.create(**kwargs)

            return True

        elif user_balance == 0:
            # Improvement. Here we need to notified via UI ? to the user that the credits are insuficient.
            logger.warning("User: {} SMS balance is 0. SMS was not send To:{}".format(
                self.obj.user.email, self.twilio_number, to_number))

        return False

    def create_contact(self, caller):
        """Return a contact created or get from caller"""
        try:
            contact, created = Contact.objects.get_or_create(
                phone=caller.number,
                user=self.obj.user,
                defaults={
                    'survey': self.obj,
                    'lead_type': 7
                }
            )
            return contact

        except Contact.MultipleObjectsReturned:
            contact = Contact.objects.filter(
                phone=caller,
                user=self.obj.user).first()

            return contact

    def exists(self):
        """return true if wrap obj is not None or empty"""
        if not self.obj:
            return False
        return True
