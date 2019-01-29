import copy

import stripe
import xlrd
from django import forms
from django.conf import settings
from django.contrib.sites.models import Site
from django.core.mail import EmailMessage
from django.db import transaction
from django.template.loader import get_template
from django.urls import reverse
from twilio.rest import Client as TwilioRestClient

from ccc.billing.models import PaymentHistory
from ccc.contacts.lead_importer import validate_email
from ccc.contacts.models import Contact, ContactProperty
from ccc.contacts.utils import clean_phone
from ccc.packages.models import TwilioNumber

ACCOUNT_SID = settings.TWILIO_SID
AUTH_TOKEN = settings.TWILIO_TOKEN
client = TwilioRestClient(ACCOUNT_SID, AUTH_TOKEN)


def onetime_charge_for_additional_numbers(user, numbers_to_charge):
    """ This creates a one-time charge for the user when buying additional
    numbers. """

    if numbers_to_charge > 0:
        stripe.api_key = settings.STRIPE_SECRET_KEY
        customer = user.customer
        stripe_customer = stripe.Customer.retrieve(customer.customer_id)
        charge = stripe.Charge.create(amount=settings.ADDITIONAL_PHONE_NUMBER_COST * numbers_to_charge, currency='usd',
                                      description='SRM Fusion additional numbers (%d)' % numbers_to_charge,
                                      customer=stripe_customer)
        PaymentHistory.objects.create(user=user, cost=charge.amount / 100.0,
                                      completed=True, payment_id=charge.id, current=True)


class XLSJobImporter(object):
    def __init__(self, excel_file):
        self.content = excel_file

    def preview(self, num_of_rows=10):
        book = xlrd.open_workbook(file_contents=self.content)
        sheet = book.sheet_by_index(0)

        rows = []
        for i in range(min(sheet.nrows, num_of_rows)):
            rows.append(sheet.row_values(i))

        return rows

    @transaction.atomic
    def import_jobs(self):
        # Open first sheet in workbook we find
        book = xlrd.open_workbook(file_contents=self.content)
        sheet = book.sheet_by_index(0)

        # Load in each row as a Job entry
        curr_row = 1
        while curr_row < sheet.nrows:
            self.read_row(sheet, curr_row)
            curr_row += 1

    def validate_all(self, col_types, col_custom_names, drop_first_row):
        return self.import_all(user=None,
                               col_types=col_types,
                               col_custom_names=col_custom_names,
                               drop_first_row=drop_first_row,
                               validate_only=True)

    def import_all(self, user, col_types, col_custom_names, drop_first_row, validate_only=False,
                   campaigns=[], groups=[]):
        book = xlrd.open_workbook(file_contents=self.content)
        sheet = book.sheet_by_index(0)

        invalid_rows = []

        start = drop_first_row and 1 or 0

        for row_index in range(start, sheet.nrows):
            invalid_cells = []
            raw_row = sheet.row_values(row_index)
            row = copy.deepcopy(raw_row)

            existing_contact = None

            try:
                phone_number, country = clean_phone(str(row[col_types.index('phone')]))
            except ValueError:
                pass  # no 'phone' column
            else:
                if phone_number:
                    existing_contact = Contact.objects.filter(phone=phone_number, user=user).first()

            try:
                email = row[col_types.index('email')]
                validate_email(email)
            except (ValueError, forms.ValidationError):
                pass  # no 'email' column or invalid
            else:
                if email:
                    existing_contact = Contact.objects.filter(email=email, user=user).first()

            if existing_contact:
                contact = existing_contact
            else:
                contact = Contact()
                contact.user = user
                contact.lead_type = 4

            contact_properties = []

            for col_index, col_type in enumerate(col_types):

                if col_type != 'None':
                    if col_type == 'phone':
                        row[col_index] = str(row[col_index])
                        phone_number, country = clean_phone(row[col_index])
                        contact.phone = phone_number
                        contact.country = country
                        if not phone_number:
                            invalid_cells.append(col_index)

                    elif col_type == 'email':
                        try:
                            validate_email(row[col_index])
                        except forms.ValidationError:
                            invalid_cells.append(col_index)
                        else:
                            contact.email = row[col_index]

                    elif col_type == 'custom':
                        cp = ContactProperty()
                        cp.name = col_custom_names[col_index]
                        cp.value = row[col_index]
                        contact_properties.append(cp)

                    else:
                        setattr(contact, col_type, row[col_index])

            if invalid_cells:
                row_result = [(row[i], None) for i in range(len(row))]
                for invalid_cell_index in invalid_cells:
                    row_result[invalid_cell_index] = (row_result[invalid_cell_index][0], True)

                invalid_rows.append([(row_index + 1, None)] + row_result)

            if not validate_only and not invalid_cells:
                # save contact and properties
                contact.save()
                for contact_property in contact_properties:
                    cp, created = ContactProperty.objects.get_or_create(contact=contact, name=contact_property.name)
                    cp.value = contact_property.value
                    cp.save()

                # add to campaigns
                for campaign in campaigns:
                    contact.campaigns.add(campaign)

                # add to groups
                for group in groups:
                    group.contacts.add(contact)

        if validate_only or invalid_cells:
            return invalid_rows
        else:
            return drop_first_row and sheet.nrows - 1 or sheet.nrows


def validate_media_absolute_url(url):
    if not url:
        return url
    if 'storage.googleapis' in url:
        if 'http' not in url[:5]:
            return 'https:{}'.format(url)
        return url
    else:
        if 'http' not in url[:5]:
            return 'https:{}{}'.format(Site.objects.get_current().domain, url)
        return url


def send_html_email(subject, _from, to, context, template):
    """Send a HTML email"""

    message = get_template(template).render(context)
    msg = EmailMessage(subject, message, to=to, from_email=_from)
    msg.content_subtype = 'html'
    msg.send()


def send_welcome_email_to_supplier(user, password, company=None, subject=None, template=None, login_url=None):
    """Send email welcome email to new Suppliers, sending login information"""
    if not subject:
        subject = "Thanks for Registration"
    from_email = "noreply@%s" % Site.objects.first().domain
    to = [user.email]
    if not template:
        template = 'emails/welcome_new_supplier.html'

    domain = "https://%s" % Site.objects.first().domain
    if login_url:
        login_url = domain + login_url
    else:
        login_url = domain + reverse('login')

    context = {
        'login_url': login_url,
        'user': user.first_name,
        'last_name': user.last_name,
        'email': user.email,
        'password': password,
        'company_name': company,
    }

    send_html_email(subject, from_email, to, context, template)
