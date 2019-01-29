import logging

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.sites.models import Site
from django.urls import reverse
from gcloud_tasks.decorators import task

from ccc.contacts.fullcontacts import FullContacts

logger = logging.getLogger(__name__)
UserModel = get_user_model()


@task(queue=settings.GOOGLE_TASK_QUEUE_DEFAULT)
def fetch_social_profiles(request, contact_id):
    """Fetch social profile from full contact api"""
    from ccc.contacts.models import Contact, RemoveDomainSearch

    logger.info("fetching social profile for contact id {}".format(contact_id))
    contact = Contact.objects.get(pk=contact_id)
    if contact.email:
        logger.info("fetching social profile for contact email {}".format(contact.email))
        fc = FullContacts()
        data = fc.get_social_profile_by_email(contact.email)
        if data:
            contact.social_profiles.create(data=data, **data)
        domain = contact.email.split("@")[1]
        if not RemoveDomainSearch.objects.filter(domain_name=domain).exists():
            data = fc.get_social_profile_by_domain(domain)
            if data:
                contact.company_social_profiles.create(data=data, **data)
    else:
        logger.info("Unable to fetch social profile for contact id {}".format(contact_id))


@task(queue=settings.GOOGLE_TASK_QUEUE_DEFAULT)
def trigger_contact_import(request, excel_file_path, user, col_types, col_custom_names, drop_first_row, campaigns,
                           groups):
    from ccc.contacts.lead_importer import XLSJobImporter
    importer = XLSJobImporter(open(excel_file_path))
    importer.import_all(user, col_types, col_custom_names, drop_first_row, campaigns=campaigns, groups=groups)


@task(queue=settings.GOOGLE_TASK_QUEUE_DEFAULT)
def create_supplier_by_contact(request, contact_id):
    """Create supplier by contact"""
    from ccc.contacts.models import Contact
    contact_instace = Contact.objects.get(pk=contact_id)
    data = {'is_supplier': True}
    phone = contact_instace.phone
    first_name = contact_instace.first_name
    last_name = contact_instace.last_name
    email = contact_instace.email
    company_name = contact_instace.company_name
    title = contact_instace.designation
    if phone:
        data.update({'phone': phone})
    if first_name:
        data.update({'first_name': first_name})
    if last_name:
        data.update({'last_name': last_name})
    if email:
        data.update({'email': email})
    if company_name:
        data.update({'company_name': company_name})
    if title:
        data.update({'title': title})
    logger.info("Contact data for supplier {}".format(data))
    password = UserModel.objects.make_random_password()
    data.update({'password': password})
    created_user = UserModel.objects.create_user(**data)
    logger.info("Supplier created by contact and email prepare")
    user = contact_instace.user
    from ccc.utils.utils import send_welcome_email_to_supplier
    send_welcome_email_to_supplier(
        created_user,
        password,
        user.company_name,
        template='ccsfusion/welcome_new_supplier.html',
        login_url=reverse('srm:users:login')
    )
    logger.info("Supplier created by contact and email sent")
    data = {
        'from_email': user.email,
        'to_email': email,
        'company': company_name,
        'subject': "Supplier Registration by contact",
        'user': user
    }
    from ccc.campaigns.models import OEmail
    OEmail.objects.create(**data)
    logger.info("Supplier created by contact is finished")


@task(queue=settings.GOOGLE_TASK_QUEUE_DEFAULT)
def send_business_card_url_task(request, contact_id):
    from ccc.contacts.models import Contact
    contact_instace = Contact.objects.get(pk=contact_id)
    to_number = contact_instace.cell_number or contact_instace.phone
    url = "https://%s%s" % (Site.objects.first().domain, contact_instace.social_url)
    text = contact_instace.get_full_name + '\n' + url + '\n' + 'Powered by LinkFusion'
    from twilio.rest import Client as TwilioRestClient
    TwilioRestClient(settings.TWILIO_SID, settings.TWILIO_TOKEN)
    twilio = TwilioRestClient(settings.TWILIO_SID, settings.TWILIO_TOKEN)
    twilio.messages.create(body=text, to=to_number.as_e164, from_=settings.TWILIO_DEFAULT_SYSTEM_NUMBER)
    logger.info("Digital Business card is sent Successfully sent")
