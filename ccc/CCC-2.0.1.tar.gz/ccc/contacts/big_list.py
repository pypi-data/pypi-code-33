from django.conf import settings
from twilio.rest import Client as TwilioRestClient

from ccc.campaigns.models import \
    OSMS  # Todo #Fixme see why in legacy code try to import Contact
from ccc.campaigns.models import UserProfile
from ccc.contacts.models import Contact

ACCOUNT_SID = settings.TWILIO_SID
AUTH_TOKEN = settings.TWILIO_TOKEN


# TODO: investigate this


def send_one(to_who, from_who, message):
    OSMS.objects.create(to=to_who, from_no=from_who, text=message, sent=True)

    client = TwilioRestClient(ACCOUNT_SID, AUTH_TOKEN)

    try:

        message = client.messages.create(body=message, to=to_who, from_=from_who)
        print('Sent YYYYYYYYYYYYYYYYYESSSSSSSSS')
    except BaseException:

        print('Not Sent')


# TODO: investigate this


def send(phone, message):
    user = UserProfile.objects.get(username='billcarter')
    total = Contact.objects.filter(user=user).count()
    contacts = Contact.objects.filter(user=user).order_by('-id')[:246]
    sent = 0
    phone = phone
    message = message
    for contact in contacts:

        OSMS.objects.create(to=contact.phone, from_no=phone, text=message, sent=True)
        # send message
        try:
            client = TwilioRestClient(ACCOUNT_SID, AUTH_TOKEN)

            print(contact.phone)
            print(phone)
            if contact.first_name:
                message = 'Hi ' + str(contact.first_name) + message

            client.messages.create(body=message,
                                   to=str(contact.phone),
                                   from_=phone)
            print('Sent to %s' % str(contact.phone))
            sent += 1

        except BaseException:
            print('Failed %s' % str(contact.phone))
    print('Sent %s' % str(sent))
    print('Sent %s' % str(total))

    print('Remaining  %s' % str(total - sent))


# TODO: investigate this


def send_mms():
    client = TwilioRestClient(ACCOUNT_SID, AUTH_TOKEN)
    message = client.messages.create(body='Test MMS with Multiple Images', to='+14803326999', from_="+14806669090",
                                     media_url=["http://nerium.com/Assets/Images/ResultsGallery/result-cust1.jpg",
                                                'http://nerium.com/Assets/Images/ResultsGallery/result-cust8.jpg',
                                                'http://nerium.com/Assets/Images/ResultsGallery/result-cust10.jpg'])

    # to="+14803326999",
    # 0705994226


# TODO: investigate this


def send_sms(to_no, msg):
    client = TwilioRestClient(ACCOUNT_SID, AUTH_TOKEN)
    message = client.messages.create(body=msg,
                                     to=to_no,
                                     from_="+14385001226",
                                     )

    # to="+14803326999",
    # 0705994226
