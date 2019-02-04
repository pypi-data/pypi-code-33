from django.conf import settings

try:
    email_contacts = settings.EMAIL_CONTACTS
except AttributeError:
    email_contacts = {"ae_report": "someone@example.com"}
