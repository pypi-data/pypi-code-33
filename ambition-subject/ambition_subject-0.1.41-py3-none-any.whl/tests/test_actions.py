from ambition_rando.tests import AmbitionTestCaseMixin
from ambition_visit_schedule import DAY1, DAY3, DAY5
from django.core.exceptions import ObjectDoesNotExist
from django.db.models.deletion import ProtectedError
from django.test import TestCase, tag, override_settings
from edc_action_item.models.action_item import ActionItem
from edc_appointment.models.appointment import Appointment
from edc_base.utils import get_utcnow
from edc_constants.constants import YES
from edc_visit_tracking.constants import SCHEDULED
from model_mommy import mommy
from model_mommy.mommy import make_recipe
from edc_reportable.units import TEN_X_9_PER_LITER


@override_settings(SITE_ID='10')
class TestActions(AmbitionTestCaseMixin, TestCase):

    def setUp(self):
        subject_screening = mommy.make_recipe(
            'ambition_screening.subjectscreening')

        options = {
            'screening_identifier': subject_screening.screening_identifier,
            'consent_datetime': get_utcnow, }
        consent = mommy.make_recipe(
            'ambition_subject.subjectconsent', **options)

        self.subject_identifier = consent.subject_identifier

        self.appointment = Appointment.objects.get(
            subject_identifier=self.subject_identifier,
            visit_code=DAY1)
        self.subject_visit = mommy.make_recipe(
            'ambition_subject.subjectvisit',
            appointment=self.appointment,
            reason=SCHEDULED)

    @tag('1')
    def test_(self):
        obj = make_recipe(
            'ambition_subject.bloodresult',
            subject_visit=self.subject_visit,
            platelets=49,
            platelets_units=TEN_X_9_PER_LITER,
            results_abnormal=YES,
            results_reportable=YES)

        try:
            ActionItem.objects.get(
                action_identifier=obj.action_identifier)
        except ObjectDoesNotExist:
            self.fail('ActionItem unexpectedly does not exist.')

        try:
            ActionItem.objects.get(
                parent_action_item__action_identifier=obj.action_identifier)
        except ObjectDoesNotExist:
            self.fail('ActionItem unexpectedly does not exist.')
        obj.save()

    @tag('1')
    def test_2(self):
        make_recipe(
            'ambition_subject.bloodresult',
            subject_visit=self.subject_visit,
            platelets=49,
            platelets_units=TEN_X_9_PER_LITER,
            results_abnormal=YES,
            results_reportable=YES)
        appointment = Appointment.objects.get(
            subject_identifier=self.subject_identifier,
            visit_code=DAY3)
        mommy.make_recipe(
            'ambition_subject.subjectvisit',
            appointment=appointment,
            reason=SCHEDULED)
        appointment = Appointment.objects.get(
            subject_identifier=self.subject_identifier,
            visit_code=DAY5)
        subject_visit = mommy.make_recipe(
            'ambition_subject.subjectvisit',
            appointment=appointment,
            reason=SCHEDULED)
        obj = make_recipe(
            'ambition_subject.bloodresult',
            subject_visit=subject_visit,
            results_abnormal=YES,
            results_reportable=YES)
        try:
            action_item = ActionItem.objects.get(
                action_identifier=obj.action_identifier)
        except ObjectDoesNotExist:
            self.fail('ActionItem unexpectedly does not exist.')
        self.assertRaises(ProtectedError, action_item.delete)
