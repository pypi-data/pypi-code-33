import hashlib
import math
import random

from accounts.models import Account as AccountModel
from cloud_tools.contrib.mail.send import send_templated_email
from django.conf import settings
from django.contrib.auth.signals import (user_logged_in, user_logged_out,
                                         user_login_failed)
from django.contrib.sites.models import Site
from django.db import models
from django.db.models import Sum
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse
from phonenumber_field.modelfields import PhoneNumberField

from ccc.users import choices
from ccc.users import signals as user_signals


class UserProfile(AccountModel):
    """Put here only logic. Not try to add fields.
    Please see Accounts package documentation"""

    class Meta:
        proxy = True

    @classmethod
    def get_instance(cls, account):
        """Return the userprofile instance from the account object"""
        return UserProfile.objects.get(email=account.email)

    @property
    def hello_test(self):
        print("Yes Im CRM!!, this is a test.")

    @property
    def balance(self):
        return self.stats()

    def usage_stats(self, campaign=None):

        return self.stats(campaign=campaign)

    def get_email_data(self, campaign=None, is_email_statics=False):
        """"""
        from ccc.campaigns.models import EmailCampaign, IEmail, OEmail
        from ccc.template_design.models import EmailAndWebAnalytics
        oemail_objects = OEmail.objects.filter(user__email=self.email)
        if is_email_statics:
            if campaign:
                oemail_objects = oemail_objects.filter(campaign=campaign)
            oemail = oemail_objects.filter(campaign__active=True).count()
            campaign_id = campaign if campaign else None
            iemail = EmailAndWebAnalytics.email_open_rate(user_id=self.id, campaign_id=campaign_id)
        else:
            ecampaign_ids = EmailCampaign.objects.filter(user__email=self.email).values_list('id', flat=True)
            iemail_objects = IEmail.objects.filter(campaign__in=ecampaign_ids)
            if campaign:
                iemail_objects = iemail_objects.filter(campaign=campaign)
                oemail_objects = oemail_objects.filter(campaign=campaign)
            iemail = iemail_objects.count()
            oemail = oemail_objects.count()
        return [oemail, iemail]

    def get_number_list(self):
        """Returns the list of numbers associated to this user instance"""
        from ccc.packages.models import TwilioNumber
        num_list = TwilioNumber.objects.filter(user__email=self.email).values_list('twilio_number', flat=True)
        return num_list

    def stats(self, campaign=None):
        """Get user stats"""
        from ccc.campaigns.models import (IVoiceCall, OVoiceCall, IMMS, OMMS, ISMS, OSMS)
        from ccc.packages.models import PurchasedPackage, Credit

        result_stats = {}

        num_list = self.get_number_list()

        i_voice_calls = IVoiceCall.objects.filter(to__in=num_list)
        o_voice_calls = OVoiceCall.objects.filter(from_no__in=num_list, charged=True)
        if campaign:
            i_voice_calls = i_voice_calls.filter(campaign=campaign)
            o_voice_calls = o_voice_calls.filter(campaign=campaign)

        vcr = i_voice_calls.aggregate(Sum('duration'))['duration__sum'] or 0
        vco = o_voice_calls.aggregate(Sum('duration'))['duration__sum'] or 0
        vco, vcr = math.ceil(vco / 60.0), math.ceil(vcr / 60.0)
        result_stats['voice_usage'] = [int(vco), int(vcr)]
        # ----------------------------------------

        imms_objects = IMMS.objects.filter(to__in=num_list)
        omms_objects = OMMS.objects.filter(from_no__in=num_list)
        if campaign:
            imms_objects = imms_objects.filter(campaign=campaign)
            omms_objects = omms_objects.filter(campaign=campaign)
        imms = imms_objects.count()
        #         omms = omms_objects.exclude(message_sid=None).filter(status='delivered').count()
        omms = omms_objects.exclude(message_sid=None).count()
        result_stats['mms_usage'] = [omms, imms]
        # ----------------------------------------

        isms_objects = ISMS.objects.filter(to__in=num_list)
        osms_objects = OSMS.objects.filter(from_no__in=num_list)
        if campaign:
            isms_objects = isms_objects.filter(campaign=campaign)
            osms_objects = osms_objects.filter(campaign=campaign)
        isms = isms_objects.count()
        osms = osms_objects.exclude(message_sid=None).filter(status='delivered').aggregate(Sum('num_segments'))['num_segments__sum'] or 0
        osms += osms_objects.filter(message_sid=None).count()  # legacy OSMS objects

        result_stats['sms_usage'] = [osms, isms]
        # ----------------------------------------
        result_stats['email_usage'] = self.get_email_data(campaign=campaign)
        # ----------------------------------------

        result_stats.update({
            'sms': 0,
            'mms': 0,
            'email': 0,
            'talktime': 0,
            'phones': 0,
        })

        package_ids = PurchasedPackage.objects.filter(user__email=self.email, approved=True, paid=True).values_list(
            'id', flat=True)
        credits = Credit.objects.filter(package__in=package_ids)

        aggregated_values = credits.aggregate(
            sms__sum=Sum('sms'),
            mms__sum=Sum('mms'),
            email__sum=Sum('email'),
            talktime__sum=Sum('talktime'),
            phones__sum=Sum('phones'))

        totals = {key: aggregated_values['%s__sum' % key] or 0 for key in ['sms', 'mms', 'email', 'talktime', 'phones']}

        if credits:
            result_stats['sms'] = totals['sms'] - (osms + isms)
            result_stats['mms'] = totals['mms'] - (omms + imms)
            result_stats['email'] = totals['email'] - (result_stats['email_usage'][0])
            result_stats['talktime'] = totals['talktime'] - int(vco + vcr)
            result_stats['voice'] = totals['talktime'] - int(vco + vcr)
            result_stats['phones'] = totals['phones'] - self.twilionumber_set.count()
        return result_stats

    def cancel_plan(self):
        """ Call this to cancel the active subscription of the user at stripe.

        This will not delete the subscription in out system.

        All the other tasks (archiving campaigns & surveys, releasing phone
        numbers etc... must be done AFTER stripe calls our
        'customer.subscription.deleted' webhook
        (packages.stripe_webhooks.SubscriptionDeletedView) """

        # Cancel stripe subscription
        customer = self.customer

        customer.auto_switch_from_trial = False
        customer.save()

        customer.cancel_stripe_subscription()
        customer.delete_stripe_card()

    def purchase_twilio_numbers(self, numbers=[]):
        """
        Allows to purchase twilio number phones, Wrapping TwilioNumber class methods.
        Returns a List of TwilioNumber instances (successfully purchased numbers).
        """
        from ccc.packages.models import TwilioNumber

        successfully_purchased_numbers = TwilioNumber.bulk_purchase_numbers(
            user_owner=self,
            phone_numbers=numbers
        )
        return successfully_purchased_numbers

    def plan_cancelled(self):
        """ This must be called after the subscription was successfully
        cancelled at stripe. (In the 'customer.subscription.deleted' webhook)

        This function must NOT be called anywhere else, because this will not
        delete the subscription at stripe, only in our system. """
        # archive all active campaigns
        campaigns = self.campaign_set.filter(active=True)
        campaigns.update(active=False, phone=None)

        # archive all surveys
        surveys = self.surveys.filter(active=True)
        surveys.update(active=False, phone=None)

        # release all phone numbers
        phones = self.twilionumber_set.all()
        phones.update(in_use=False)

        for phone in phones:
            # async task
            phone.task_release_twilio_number()

        # Delete PurchasedPackages
        self.purchasedpackage_set.all().delete()

        # Clear payment reminders
        if self.payment_failed or self.next_payment_attempt:
            self.next_payment_attempt = None
            self.payment_failed = False
            self.save()

    def create_activation_code(self):
        """This generate an activation code to the user"""
        ActivationCode.objects.create(user=self)

    @property
    def parents(self):
        current = self
        parents = list()
        while True:
            if current.parent is None:
                return parents
            current = current.parent
            parents.append(current)


class UserContactNo(models.Model):
    """Hierarchy from AccountModel base. Accounts package"""
    user = models.ForeignKey(settings.ACCOUNT_USER_PROXY_MODEL, on_delete=models.CASCADE)
    contact_no = PhoneNumberField(null=True, blank=True)
    contact_number_sid = models.CharField(max_length=50, blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)

    def __str__(self):
        return self.contact_number


class ActivationCode(models.Model):
    user = models.ForeignKey(settings.ACCOUNT_USER_PROXY_MODEL, on_delete=models.CASCADE)
    token = models.CharField(max_length=255, unique=True)
    expired = models.BooleanField(default=False)
    created_at = models.DateField(auto_now_add=True)
    token_type = models.CharField(max_length=1, choices=choices.TOKEN, default=1)

    def __str__(self):
        return self.user.email

    def save(self, *args, **kwargs):
        # Make the activation token
        salt = hashlib.sha1(str(random.random()).encode('utf-8')).hexdigest()[:5]
        username = self.user.email.encode('utf-8')
        token = hashlib.sha1((salt + str(username)).encode('utf-8')).hexdigest()
        if not self.token:
            self.token = token
        super(ActivationCode, self).save(*args, **kwargs)

    def send_instructions_to_user(self):
        """Send the email activation instructions to the User"""
        domain_name = Site.objects.get_current().domain

        activation_url = "https://{}{}?activation_code={}".format(domain_name, reverse('srm:users:users_confirm'), self.token)
        context = {
            'user_fullname': self.user.first_name,
            'activation_code': self.token,
            'activation_link': activation_url,
            'hostname': activation_url
        }

        send_templated_email(
            subject=settings.EMAILS_TO_USERS['ACTIVATION']['SUBJECT'],
            email_body=settings.EMAILS_TO_USERS['ACTIVATION']['TEMPLATE'],
            email_context=context,
            recipients=self.user.email,
            render_body_to_string=True
        )


class ResetCode(models.Model):
    user = models.ForeignKey(settings.ACCOUNT_USER_PROXY_MODEL, on_delete=models.CASCADE)
    token = models.CharField(max_length=255, unique=True)
    expired = models.BooleanField(default=False)
    created_at = models.DateField(auto_now_add=True)
    token_type = models.CharField(max_length=1, choices=choices.TOKEN, default=1)

    def __str__(self):
        return self.user.email

    @property
    def password_change_link(self):
        """Returns the absolute password change URL"""
        domain_name = Site.objects.get_current().domain
        link = "https://{}{}".format(domain_name,
                                     reverse('srm:users:new_password', kwargs={'activation_key': self.token}))
        return link

    def save(self, *args, **kwargs):
        # Make the activation token#
        salt = hashlib.sha1(str(random.random()).encode('utf-8')).hexdigest()[:5]
        email = self.user.email.encode('utf-8').decode('utf-8')
        token = hashlib.sha1(str(salt + email).encode('utf-8')).hexdigest()
        if not self.token:
            self.token = token
        super(ResetCode, self).save(*args, **kwargs)

    def send_email_reset_password(self):
        """Send email instructions to reset password to the associated User"""
        from cloud_tools.contrib.mail.send import send_templated_email

        # Sending instructions to the user...
        send_templated_email(
            recipients=self.user.email,
            subject=settings.EMAILS_TO_USERS['RESET_PASSWORD']['SUBJECT'],
            email_body=settings.EMAILS_TO_USERS['RESET_PASSWORD']['TEMPLATE'],
            render_body_to_string=True,
            email_context={'user_fullname': self.user.first_name, 'password_change_link': self.password_change_link}
        )

        return True


class OTPStore(models.Model):
    """Model to store OTP(One time password) with respective to mobile numbers
    """
    otp = models.CharField(max_length=10, null=False, blank=False)
    phone_no = models.CharField(max_length=15, null=False, blank=False, unique=True)
    timestamp = models.DateTimeField(auto_now_add=True, null=True, blank=True)


class AuditEntry(models.Model):
    action = models.CharField(max_length=64)
    ip = models.GenericIPAddressField(null=True)
    username = models.CharField(max_length=256, null=True)

    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return '{0} - {1} - {2}'.format(self.action, self.username, self.ip)


@receiver(user_logged_in)
def user_logged_in_callback(sender, request, user, **kwargs):
    if settings.AUDIT_ENTRY_ENABLED:
        ip = request.META.get('HTTP_X_REAL_IP')
        AuditEntry.objects.create(action='user_logged_in', ip=ip, username=user.email)


@receiver(user_logged_out)
def user_logged_out_callback(sender, request, user, **kwargs):
    if settings.AUDIT_ENTRY_ENABLED:
        ip = request.META.get('HTTP_X_REAL_IP')
        AuditEntry.objects.create(action='user_logged_out', ip=ip, username=user.email)


@receiver(user_login_failed)
def user_login_failed_callback(sender, credentials, **kwargs):
    if settings.AUDIT_ENTRY_ENABLED:
        AuditEntry.objects.create(action='user_login_failed', username=credentials.get('email', None))


post_save.connect(user_signals.signal_create_user_profile, sender=UserProfile)
post_save.connect(user_signals.signal_send_activation_code_email, sender=ActivationCode)
post_save.connect(user_signals.signal_for_reset_password, sender=ResetCode)
