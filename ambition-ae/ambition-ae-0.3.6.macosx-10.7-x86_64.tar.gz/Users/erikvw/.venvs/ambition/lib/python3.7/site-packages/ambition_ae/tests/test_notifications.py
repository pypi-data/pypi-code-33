from ambition_rando.tests import AmbitionTestCaseMixin
from django.contrib.auth.models import User, Permission
from django.core import mail
from django.core.management.color import color_style
from django.test import TestCase, tag
from edc_constants.constants import YES, NO, NOT_APPLICABLE
from edc_list_data.site_list_data import site_list_data
from edc_notification import site_notifications
from edc_registration.models import RegisteredSubject
from model_mommy import mommy

from ..notifications import AeSusarNotification

style = color_style()


class TestNotifications(AmbitionTestCaseMixin, TestCase):
    @classmethod
    def setUpClass(cls):
        site_list_data.autodiscover()
        super().setUpClass()

    def setUp(self):

        self.user = User.objects.create(
            username="erikvw", is_staff=True, is_active=True
        )
        self.subject_identifier = "1234"
        permissions = Permission.objects.filter(
            content_type__app_label="ambition_ae",
            content_type__model__in=["aeinitial", "aetmg"],
        )
        for permission in permissions:
            self.user.user_permissions.add(permission)

        self.subject_identifier = "12345"
        RegisteredSubject.objects.create(subject_identifier=self.subject_identifier)

        self.assertEqual(len(mail.outbox), 0)
        site_notifications._registry = {}
        site_notifications.models = {}
        site_notifications.register(AeSusarNotification)
        site_notifications.update_notification_list()
        self.assertTrue(site_notifications.loaded)

    def test_susar(self):

        mommy.make_recipe(
            "ambition_ae.aeinitial",
            subject_identifier=self.subject_identifier,
            susar=YES,
            susar_reported=NO,
            user_created="erikvw",
        )

        self.assertEqual(len(mail.outbox), 1)

    def test_susar_updates(self):

        ae_initial = mommy.make_recipe(
            "ambition_ae.aeinitial",
            subject_identifier=self.subject_identifier,
            susar=YES,
            susar_reported=NO,
            user_created="erikvw",
        )

        self.assertEqual(len(mail.outbox), 1)

        ae_initial.save()

        self.assertEqual(len(mail.outbox), 1)

        ae_initial.susar_reported = YES
        ae_initial.save()

        self.assertEqual(len(mail.outbox), 1)

        ae_initial.susar = NO
        ae_initial.susar_reported = NOT_APPLICABLE
        ae_initial.save()

        self.assertEqual(len(mail.outbox), 1)

        ae_initial.susar = YES
        ae_initial.susar_reported = NO
        ae_initial.save()

        self.assertEqual(len(mail.outbox), 2)

    def test_susar_text(self):
        mommy.make_recipe(
            "ambition_ae.aeinitial",
            subject_identifier=self.subject_identifier,
            susar=YES,
            susar_reported=NO,
            user_created="erikvw",
        )

        self.assertIn("a SUSAR report is due", mail.outbox[0].subject)
        self.assertIn(
            "suspected unexpected serious adverse reaction", mail.outbox[0].body
        )

    def test_susar_manually(self):
        ae_initial = mommy.make_recipe(
            "ambition_ae.aeinitial",
            subject_identifier=self.subject_identifier,
            susar=YES,
            susar_reported=NO,
            user_created="erikvw",
        )

        AeSusarNotification().notify(instance=ae_initial, fail_silently=True)

        self.assertEqual(len(mail.outbox), 2)
