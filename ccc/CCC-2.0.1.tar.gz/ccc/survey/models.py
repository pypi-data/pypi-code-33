import re
import urllib.parse as urlparse
from urllib.parse import urlencode

from django.conf import settings
from django.db import models
from django.db.models import Max, F
from django.db.models.query_utils import Q
from django.db.models.signals import pre_delete, post_save, m2m_changed
from django.dispatch import receiver
from django.urls import reverse
from django.utils.http import int_to_base36
from model_utils import Choices
from model_utils.models import TimeStampedModel

from ccc.campaigns.utils.shortcut import shorten_url

GRUBER_URLINTEXT_PAT = re.compile(
    r'(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:\'".,<>?\xab\xbb\u201c\u201d\u2018\u2019]))')


class Survey(TimeStampedModel):
    """Survey Model representation"""
    title = models.CharField(max_length=255)
    phone = models.ForeignKey('packages.TwilioNumber', related_name='surveys', null=True, blank=True,
                              on_delete=models.SET_NULL)

    user = models.ForeignKey(settings.ACCOUNT_USER_PROXY_MODEL, related_name='surveys', on_delete=models.CASCADE)

    active = models.BooleanField(default=True)

    campaign = models.ForeignKey("campaigns.Campaign", null=True, blank=True, on_delete=models.SET_NULL)

    voice_greeting_original = models.FileField(
        verbose_name='Voice Greeting',
        upload_to='surveys/voice',
        blank=True,
        null=True)

    voice_greeting_converted = models.FileField(
        upload_to='surveys/voice',
        blank=True,
        null=True)

    greeting_text = models.TextField(blank=True, null=True)
    last_message = models.TextField(blank=True, null=True)

    objects = models.Manager()

    class Meta:
        ordering = ("-created",)

    def __str__(self):
        return self.title

    @property
    def voice_greeting(self):
        return self.voice_greeting_converted or \
               self.voice_greeting_original

    def archived(self):
        """Archived the current survey"""
        if self.phone:
            self.phone.idle()  # released number
        self.phone = None
        self.active = False
        self.save()

    def un_archived(self):
        """Archived the current survey"""
        self.active = True
        self.save()

    def update_twilio_urls(self):
        """Apply the default survey handler to the current phone number"""
        twilio_number = self.phone
        twilio_number.voice_url = reverse(settings.TWILIO_SURVEY_VOICE_HANDLER_URL_NAME)
        twilio_number.sms_url = reverse(settings.TWILIO_SURVEY_SMS_HANDLER_URL_NAME)
        twilio_number.save()
        # call async task
        twilio_number.task_update_twilio_urls()

        return True


class QuestionManager(models.Manager):

    def question_for_contact(self, survey, contact):
        last_answer = contact.contact_useranswer.filter(
            question__survey=survey).order_by('created').last()

        if not last_answer:
            return self.root_question()

        try:
            last_answer.mcqanswer
        except McqAnswer.DoesNotExist:
            try:
                last_answer.textanswer
            except TextAnswer.DoesNotExist:
                return
            else:
                next_question = last_answer.textanswer.question.next_questions.first()
                if next_question:
                    return next_question
                # Child questions are finished so moving to parent questions
                all_asked_ques = contact.contact_useranswer.filter(
                    question__survey=survey).values_list('question__id', flat=True)
                question = Question.objects.filter(
                    survey=survey).filter(
                    in_response_of=None).exclude(id__in=all_asked_ques).first()
                return question
        else:
            answer_choice = last_answer.mcqanswer.answer_choice
            if answer_choice.should_halt:
                # If the user specifies that the survey should halt once the user selects that particular option
                # return nothing
                return
            next_question = answer_choice.child_questions.first()
            if not next_question:
                # Child questions are finished so moving to parent questions
                all_asked_ques = contact.contact_useranswer.filter(
                    question__survey=survey).values_list('question__id', flat=True)
                next_question = last_answer.mcqanswer.answer_choice.child_questions.first()
                parent_question = last_answer.question.in_response_of.first()
                child_ques = None
                if parent_question and parent_question.child_questions:
                    child_ques = parent_question.child_questions.exclude(id__in=all_asked_ques)
                if child_ques:
                    return child_ques[0]
                question = Question.objects.filter(
                    survey=survey).filter(
                    in_response_of=None).exclude(id__in=all_asked_ques).first()

                return question
            return last_answer.mcqanswer.answer_choice.child_questions.first()

    def root_question(self):
        # TODO FIX: This assumes that self.get_queryset has alrady filtered for
        # survey
        return self.get_queryset().filter(in_response_of=None).last()

    def last_question(self):
        last_question = self.root_question()
        results = last_question
        while results:
            q = Q(in_response_of__in=last_question.answer_choices.all()) | \
                Q(in_response_of_question=last_question)
            results = self.get_queryset().filter(q).distinct()
            if results:
                last_question = results.last()
        return last_question

    # TODO: improve this logic. this is query intesive and a little buggy
    def all_questions(self):
        all_questions = []
        last_question = self.root_question()
        root_question = self.root_question()
        if last_question:
            all_questions.append(last_question)
            results = last_question
            while results:
                q = Q(in_response_of__in=last_question.answer_choices.all()) | \
                    Q(in_response_of_question=last_question)
                results = self.get_queryset().filter(q).distinct()
                for question in results:
                    all_questions.append(question)
                    last_question = results.last()
            all_response_question = Question.objects.filter(
                survey=root_question.survey).filter(
                in_response_of=None).exclude(id__in=[x.id for x in all_questions])
            if all_response_question:
                all_questions.extend(all_response_question)
                all_questions = list(set(all_questions))
        return all_questions


class Question(TimeStampedModel):
    TYPES = Choices(
        ('mcq', 'Multiple Choice'),
        ('text', 'Text based response')
    )
    CONTACT_MAPPINGS = Choices(
        ('company_name', 'Company Name'),
        ('designation', 'Designation'),
        ('email', 'Email'),
        ('first_name', 'First Name'),
        ('last_name', 'Last Name'),
        ('state', 'State'),
        ('zip', 'Zip'),
        ('country', 'Country'),
    )
    survey = models.ForeignKey('Survey', related_name='questions', on_delete=models.CASCADE)
    question = models.TextField()

    in_response_of = models.ManyToManyField("AnswerChoice", related_name='child_questions', blank=True)

    in_response_of_question = models.ManyToManyField(
        "Question", related_name='next_questions', blank=True, help_text='Used for text based questions')

    delay = models.PositiveIntegerField(default=0, help_text="In seconds")
    question_type = models.CharField(max_length=100, choices=TYPES,
                                     default='mcq')
    contact_mapping = models.CharField(max_length=100, choices=CONTACT_MAPPINGS, null=True, blank=True,
                                       verbose_name="Map response to contact field")
    order = models.IntegerField(default=0)

    objects = QuestionManager()

    class Meta:
        ordering = ("-order", "-created",)

    def __str__(self):
        return self.question

    @classmethod
    def clean_delay_value(cls, delay, schedular_step):
        """
        The delay value is calculated of this way: delay * schedular_step
        This will need call explicitly. We following the legacy code that clearly have a bad design,
        but we don't have time for refactoring.
        Used to avoid repeat the code on diferent parts...#DRY
        """
        return int(delay) * int(schedular_step)

    @property
    def schedular_step(self):
        """Translate delay(seconds) to the respective schedular step options: inmediatly, hour, minute, seconds"""
        _, schedular_step = self.get_delay_and_scheduled_step()
        return schedular_step

    @property
    def delay_value(self):
        """translate delay secons to the initial value selected by the user"""
        delay, _ = self.get_delay_and_scheduled_step()
        return delay

    def get_delay_and_scheduled_step(self):
        """This a legacy code. We move this to the model...to avoid repeat this coded constantly"""
        schedular_step = 0
        delay = self.delay

        if delay >= 86400:
            schedular_step = 86400
            delay = delay / 86400

        elif delay >= 3600:
            schedular_step = 3600
            delay = delay / 3600

        elif delay >= 60:
            schedular_step = 60
            delay = delay / 60

        return delay, schedular_step

    def get_message(self, contact):
        message = self.question

        for answer in self.answer_choices.all():
            message += "\n{0}. {1}".format(answer.code, answer.answer)

        mgroups = GRUBER_URLINTEXT_PAT.findall(message)
        for urls in mgroups:
            for url in urls:
                if url.strip() and \
                    not url.startswith("http://goo.gl") and \
                    not url.startswith("https://goo.gl"):
                    short_url = shorten_url(self.url_for_contact(url, contact))
                    survey_link, created = SurveyLink.objects.get_or_create(
                        contact=contact,
                        question=self,
                        long_url=url,
                        short_url=short_url)
                    message = message.replace(url, short_url)

        return message

    def url_for_contact(self, url, contact):
        params = {
            'utm_source': 'ccc',
            'utm_medium': 'sms',
            'utm_content': int_to_base36(contact.pk),
            'utm_campaign': int_to_base36(self.pk)
        }
        url_parts = list(urlparse.urlparse(url))
        query = dict(urlparse.parse_qsl(url_parts[4]))
        query.update(params)
        url_parts[4] = urlencode(query)
        return urlparse.urlunparse(url_parts)


# @receiver(post_save, sender=Question, dispatch_uid='question_save_signal')
def auto_increase_order_question_on_m2m_added(sender, instance, **kwargs):
    if kwargs['action'] == 'post_add':
        parent = list(kwargs.get('pk_set'))[0]
        if isinstance(instance, Question):
            same_survey_questions = Question.objects.get(pk=parent).next_questions.exclude(pk=instance.id)
        else:
            same_survey_questions = AnswerChoice.objects.get(pk=parent).child_questions.exclude(pk=instance.id)
        if same_survey_questions.exists():
            last_order = same_survey_questions.order_by('-order').first().order
            instance.order = last_order + 1
            instance.save()


def auto_increase_order_question_on_save(sender, instance, **kwargs):
    if kwargs.get('created'):
        last_order = Question.objects.filter(survey=instance.survey_id, in_response_of_question__isnull=True,
                                             in_response_of__isnull=True).exclude(id=instance.id)\
            .order_by('-order').first().order
        instance.order = last_order + 1
        instance.save()


post_save.connect(auto_increase_order_question_on_save, sender=Question)
m2m_changed.connect(auto_increase_order_question_on_m2m_added, sender=Question.in_response_of.through)
m2m_changed.connect(auto_increase_order_question_on_m2m_added, sender=Question.in_response_of_question.through)


class AnswerChoice(TimeStampedModel):
    question = models.ForeignKey('Question', related_name='answer_choices', on_delete=models.CASCADE)
    answer = models.CharField(max_length=255)
    should_halt = models.BooleanField(default=False)
    code = models.PositiveIntegerField()

    class Meta:
        unique_together = (("question", "code"),)
        ordering = ("code",)

    def __str__(self):
        return "{}-{}-{}".format(self.code, self.question, self.answer)

    def save(self, *args, **kwargs):
        if self.pk is None:
            # Generate a unique code for each answer
            # unique within answers of a question
            last_code = AnswerChoice.objects.filter(
                question=self.question).aggregate(Max('code')).get('code__max')
            if last_code is None:
                last_code = 0
            self.code = last_code + 1
        super(AnswerChoice, self).save(*args, **kwargs)

    def get_following_question(self):
        return self.child_questions.last()


class UserAnswer(TimeStampedModel):
    question = models.ForeignKey("Question", related_name="question_%(class)s", on_delete=models.CASCADE)
    contact = models.ForeignKey("contacts.Contact", related_name='contact_%(class)s', on_delete=models.CASCADE)

    class Meta:
        unique_together = (("question", "contact"),)
        ordering = ("-created",)

    def __str__(self):
        return "%s - %s" % (self.contact.first_name, self.question)


class McqAnswer(UserAnswer):
    answer_choice = models.ForeignKey("AnswerChoice", related_name='user_answers', on_delete=models.CASCADE)

    class Meta:
        ordering = ("-created",)

    def __str__(self):
        return "%s - %s" % (self.contact.first_name, self.answer_choice.answer)


class TextAnswer(UserAnswer):
    answer = models.CharField(max_length=1000)

    class Meta:
        ordering = ("-created",)

    def __str__(self):
        return "%s - %s" % (self.contact.first_name, self.question.question)


class SurveyLink(TimeStampedModel):
    contact = models.ForeignKey("contacts.Contact", related_name='contact_links', on_delete=models.CASCADE)
    question = models.ForeignKey("Question", related_name='question_links', on_delete=models.CASCADE)
    long_url = models.CharField(max_length=250)
    short_url = models.CharField(max_length=250)

    def __str__(self):
        return self.long_url


@receiver(pre_delete, sender=Question, dispatch_uid='question_delete_signal')
def log_deleted_question(sender, instance, using, **kwargs):
    for parent in instance.in_response_of_question.all():
        for next_question in instance.next_questions.all():
            instance.next_questions.remove(next_question)
            parent.next_questions.add(next_question)
    order = instance.order
    # Re order the existing questions
    Question.objects.filter(survey=instance.survey, order__gt=order).update(order=F('order') - 1)


class SurveyMappedKeywords(models.Model):
    """Class to store mapped keywords with campaign
    """
    keyword = models.CharField(max_length=250, null=True, blank=True)
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
