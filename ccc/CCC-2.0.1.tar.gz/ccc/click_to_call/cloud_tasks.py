import logging
import math
from collections import namedtuple
from logging import getLogger
from uuid import uuid4

from django.conf import settings
from django.contrib.sites.models import Site
from django.core.files import File
from django.template import Context, Template
from django.urls import reverse
from django.utils.six import BytesIO
from gcloud_tasks.decorators import task
from pydub import AudioSegment

from ccc.campaigns.cloud_tasks import voice_call
from ccc.campaigns.models import OSMS, OVoiceCall
from ccc.campaigns.utils.shortcut import audio_conversion
from ccc.click_to_call.models import (AssociateMasterList, AutoDialerList,
                                      PersonalizedMessage, RealPhoneValidation)
from ccc.click_to_call.phone_utils import clean_phone_number
from ccc.contacts.models import Contact
from ccc.utils.utils import validate_media_absolute_url

log = getLogger(__name__)

Dialer = namedtuple('Dialer', ['first_name', 'last_name', 'phone_number', 'city', 'state'])


class DialListRow(object):
    def __init__(self, rows):
        self.rows = rows

    def get(self, index):
        try:
            return self.rows[index]
        except Exception:
            return ''

    @property
    def first_name(self):
        return self.get(0)

    @property
    def last_name(self):
        return self.get(1)

    @property
    def phone_number(self):
        phone = self.get(2)

        if isinstance(phone, float):
            phone = str(int(phone))
        else:
            phone = str(phone)
        return phone

    @property
    def city(self):
        return self.get(3)

    @property
    def state(self):
        return self.get(4)


def save_auto_dialer(kwargs):
    """Save auto dialer..|"""
    return AutoDialerList.objects.create(**kwargs)


def get_kwargs(dialer):
    return {
        'phone_number': dialer.phone_number,
        'first_name': dialer.first_name,
        'last_name': dialer.last_name,
    }


@task(queue=settings.GOOGLE_TASK_QUEUE_DEFAULT)
def save_dialer_list(request, m_list_id, dialers):
    """Real Phone validation, received a dialer list obj"""
    master_list = AssociateMasterList.objects.get(id=m_list_id)
    master_list_has_errors = True

    # Todo: pending improvement to avoid hit database for each register.
    dialer_list = list()
    try:
        for dialer in dialers:
            dialer = Dialer(*dialer)
            if len(dialer.phone_number) > 0:

                phone, err = clean_phone_number(dialer.phone_number)
                if err:
                    logging.info('[INFO]:' + err.__str__())

                    kwargs = get_kwargs(dialer)

                    kwargs['associated_to'] = master_list
                    kwargs['msg_err'] = err
                    kwargs['phone_status'] = 'invalid-phone'
                    kwargs['phone_type'] = 'invalid'
                    kwargs['phone_carrier'] = 'unknown'
                    kwargs['phone_cname'] = 'unknown'
                    kwargs['is_valid'] = False

                    dialer_list.append(AutoDialerList(**kwargs))
                    # save_auto_dialer(kwargs)

                elif phone and not err:
                    try:
                        real_phone, created = RealPhoneValidation.objects.get_or_create(
                            phone_number=phone.national_number,
                            defaults={'phone_number': phone.national_number, 'phone_country_code': phone.country_code})

                        # save dialer
                        kwargs = get_kwargs(dialer)
                        kwargs['associated_to'] = master_list
                        kwargs['msg_err'] = real_phone.error_text
                        kwargs['phone_status'] = real_phone.phone_status
                        kwargs['phone_type'] = real_phone.phone_type
                        kwargs['phone_carrier'] = real_phone.phone_carrier
                        kwargs['phone_cname'] = real_phone.phone_cname
                        kwargs['phone_friendly_number'] = real_phone.phone_friendly_number
                        kwargs['is_valid'] = real_phone.is_valid()

                        dialer_list.append(AutoDialerList(**kwargs))

                    except Exception as e:
                        logging.error(e.__str__())

                        master_list_has_errors = True
                        kwargs = get_kwargs(dialer)
                        kwargs['associated_to'] = master_list
                        kwargs['msg_err'] = "Service unavailable, contact support."
                        kwargs['phone_status'] = 'server-unavailable'
                        kwargs['phone_type'] = 'unknown'
                        kwargs['phone_carrier'] = 'unknown'
                        kwargs['phone_cname'] = 'unknown'
                        kwargs['is_valid'] = False

                        dialer_list.append(AutoDialerList(**kwargs))

        AutoDialerList.objects.bulk_create(dialer_list)

        master_list.has_errors = master_list_has_errors
        master_list.save()

    except Exception as exc:
        logging.fatal(exc.__str__())
        # return HttpResponse no 200Ok
        return
    finally:
        master_list.is_import_complete = True
        master_list.save()

    return master_list


@task(queue=settings.GOOGLE_TASK_QUEUE_DEFAULT)
def save_call_recording(request, url, o_voice_id):
    import requests
    import tempfile
    wav = requests.get(url)
    original = AudioSegment.from_wav(BytesIO(wav.content))
    mp3 = File(original.export("{0}.mp3".format(uuid4().hex), format="mp3"))
    o_voice = OVoiceCall.objects.get(pk=o_voice_id)
    o_voice.recording = mp3
    temp = tempfile.TemporaryFile()
    temp.write(wav.content)
    temp.seek(0)
    o_voice.recording_wav.save(uuid4().hex + '.wav', temp)
    o_voice.save()
    temp.close()
    get_call_sentiments(request=None, o_voice_id=o_voice_id)
    return mp3


def get_call_sentiments(request, o_voice_id):
    import requests
    o_voice = OVoiceCall.objects.get(pk=o_voice_id)
    response = requests.post(url=settings.SENTIMENTS_URL,
                             json={'uri': validate_media_absolute_url(o_voice.recording_wav.url)})
    print(response.status_code)
    print(response.json())
    if response.status_code == 200:
        data = response.json()
        o_voice.recording_sentiment_score = data.get('score')
        o_voice.recording_sentiment_magnitude = data.get('magnitude')
        o_voice.recording_text = data.get('text')
        o_voice.save()


@task(queue=settings.GOOGLE_TASK_QUEUE_DEFAULT)
def convert_audio_personalized_message(request, msg_id):
    pm = PersonalizedMessage.objects.get(pk=msg_id)
    if pm.audio:
        audio = audio_conversion(pm.audio)
        pm.audio = audio
        pm.audio_processed = True
        pm.save()
        return pm


@task(queue=settings.GOOGLE_TASK_QUEUE_DEFAULT)
def throttle_send_personalized_messages(request, contact_ids, type_, from_, personal_msg_id, at_a_time=20,
                                        interval_mins=20):
    if not isinstance(contact_ids, list):
        contact_ids = [contact_ids]
    batch_count = len(contact_ids) / at_a_time
    batch_count = math.ceil(batch_count)

    for i in range(0, batch_count):
        start_index = i * at_a_time
        end_index = i * at_a_time + at_a_time
        range_to_send = contact_ids[start_index:end_index]
        delay = i * interval_mins * 60
        send_bc_personalized_messages(contact_ids=range_to_send, type_=type_, from_=from_,
                                      personal_msg_id=personal_msg_id).execute(seconds=delay)


@task(queue=settings.GOOGLE_TASK_QUEUE_DEFAULT)
def send_bc_personalized_messages(request, contact_ids, type_, from_, personal_msg_id):
    if not isinstance(contact_ids, list):
        contact_ids = [contact_ids]
    hostname = Site.objects.get_current().domain
    relative_callback = reverse('srm:api_marketing:autodialer:twilio-get-content',
                                kwargs={'pk': personal_msg_id})
    callback_url = 'https://{}{}'.format(hostname, relative_callback)
    personal_msg = PersonalizedMessage.objects.get(pk=personal_msg_id)
    contacts = Contact.objects.filter(pk__in=contact_ids, phone__isnull=False)
    if type_ == 'voice':
        for contact in contacts:
            o_voice = OVoiceCall.objects.create(from_no=from_, to=contact.phone)
            voice_call(url=callback_url, method='GET', to_phone=contact.phone.as_e164, from_phone=from_,
                       o_voice_id=o_voice.id).execute()
    else:
        for contact in contacts:
            text = Template(personal_msg.text).render(Context(contact.template_context))
            OSMS.objects.create(to=contact.phone, from_no=from_, text=text)
