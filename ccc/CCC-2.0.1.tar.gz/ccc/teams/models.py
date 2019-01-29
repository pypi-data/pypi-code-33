import hashlib
import random

from django.conf import settings
from django.contrib.sites.models import Site
from django.db import models
from django.urls import reverse

from ccc.packages.models import TwilioNumber
from ccc.teams import cloud_tasks


class Team(models.Model):
    """
    Model to store team information

    """
    phone = models.ForeignKey(TwilioNumber, blank=True, null=True, on_delete=models.SET_NULL)
    name = models.CharField(max_length=100, unique=True)
    description = models.CharField(max_length=255)
    creator = models.ForeignKey(settings.ACCOUNT_USER_PROXY_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    active = models.BooleanField(default=True)
    date_created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    @property
    def available(self):
        # get the smaller number in list
        team_members = TeamMember.objects.filter(team=self)
        team_members = team_members.exclude(user=None)

        my_turn = team_members[0].repeat
        user = None
        for i in team_members:
            if my_turn >= i.repeat:
                my_turn = i.repeat
                user = i

        return user

    def members(self):
        team_members = TeamMember.objects.filter(team=self)
        return team_members

    def add_member(self, name, email=None, phone=None, team_creator=False, order=0):
        """Add a new member tot this team."""
        defaults = {
            'team': self,
            'nick_name': name,
            'personal_phone': phone,
            'email': email,
            'team_creator': team_creator,
            'order': order,
            'token': self.generate_hash_token(name)
        }
        # creating the new member associated to this team...
        new_member = TeamMember.objects.create(**defaults)
        # Sending email and SMS invitation to the new member...
        new_member.task_send_email_invite_team()
        new_member.task_send_sms_invite_team()

    def send_email_invitation(self, name, email, phone, team_creator=False):
        """Send an email invitation to the new member"""
        defaults = {
            'team': self, 'nickname': name,
            'personal_phone': phone, 'email': email,
            'team_creator': team_creator, 'order': 0,
            'token': self.generate_hash_token(name)
        }
        new_member = TeamMember.objects.create(**defaults)
        new_member.task_send_email_invitation()

    @staticmethod
    def generate_hash_token(name):
        """Receives a string name and generates and returns a random token."""
        salt = hashlib.sha1((str(random.random())).encode('utf-8')).hexdigest()[:5]
        u_name = name.encode('utf-8')
        token = hashlib.sha1((salt + str(u_name)).encode('utf-8')).hexdigest()
        return token


class TeamMember(models.Model):
    nick_name = models.CharField(max_length=50, blank=True, null=True)
    user = models.ForeignKey(settings.ACCOUNT_USER_PROXY_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    phone = models.ForeignKey(TwilioNumber, blank=True, null=True, on_delete=models.CASCADE)
    email = models.CharField(max_length=255, blank=True, null=True)
    personal_phone = models.CharField(max_length=50, blank=True, null=True)
    order = models.IntegerField(default=0)
    repeat = models.IntegerField(default=0)
    latest = models.BooleanField(default=True)
    team_credit = models.BooleanField(default=False)
    team_creator = models.BooleanField(default=False)
    token = models.CharField(blank=True, null=True, max_length=255)
    date_created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.nick_name

    def save(self, *args, **kwargs):
        order = TeamMember.objects.filter(team=self.team).count()
        self.order = order + 1
        super(TeamMember, self).save(*args, **kwargs)

    def get_invite_url(self):
        domain_name = Site.objects.get_current().domain
        link = reverse('srm:teams:accept_invite', kwargs={'token': self.token})
        return 'https://{}{}'.format(domain_name, link)

    def api_twilio(self):
        from twilio.rest import Client as TwilioRestClient
        return TwilioRestClient(settings.TWILIO_SID, settings.TWILIO_TOKEN)

    def send_sms_invite_team(self):
        """Send SMS invite. membership invitation"""
        sms_message = "Hi {}, You have been requested to join the {}. Reply with \
                                                1 to Accept\
                                                2 to Reject".format(self.nick_name, self.team.name)
        twilio = self.api_twilio()
        twilio.messages.create(
            body=sms_message, to=self.personal_phone,
            from_=settings.TWILIO_DEFAULT_SYSTEM_NUMBER
        )
        return True

    def send_email_invite_team(self):
        """Send email invite team. Membership invitation."""
        from cloud_tools.contrib.mail.send import send_templated_email

        email_template = settings.EMAILS_TO_USERS['INVITE_TEAM_MEMBERSHIP']['TEMPLATE']
        subject = settings.EMAILS_TO_USERS['INVITE_TEAM_MEMBERSHIP']['SUBJECT']

        context = {
            'subject': subject,
            'username': self.nick_name,
            'team_name': self.team.name,
            'token': self.token,
            'invite_url': self.get_invite_url()
        }

        send_templated_email(
            recipients=self.email, subject=subject, email_body=email_template,
            render_body_to_string=True, email_context=context
        )
        return True

    def task_send_email_invite_team(self):
        """Executes send email invite team in async way."""
        cloud_tasks.task_send_email_invite_team(member_id=self.id).execute()

    def task_send_sms_invite_team(self):
        if self.personal_phone:
            cloud_tasks.task_send_sms_invite_team(member_id=self.id).execute()
        return False


class Tutorial(models.Model):
    subject = models.CharField(max_length=64)
    description = models.TextField(null=True, blank=True)
    category = models.CharField(max_length=255, null=True, blank=True)
    tag = models.CharField(max_length=255, null=True, blank=True)
    date_created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.subject

    class Meta:
        db_table = 'tutorial'


class VideoFile(models.Model):
    tutorial = models.ForeignKey(Tutorial, on_delete=models.CASCADE)
    video = models.FileField(upload_to='campaigns/tutorials')
    description = models.TextField(null=True, blank=True)
    category = models.CharField(max_length=255, null=True, blank=True)
    tag = models.CharField(max_length=255, null=True, blank=True)
    date_created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.subject

    class Meta:
        db_table = 'video_tutorial'
