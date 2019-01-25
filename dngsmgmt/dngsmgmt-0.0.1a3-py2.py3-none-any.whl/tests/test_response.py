from django.urls import reverse
from django.test import TestCase

from rest_framework.test import APIClient


class HealthResponseTestCase(TestCase):

    def setUp(self):
        self.client = APIClient()

    def test_health(self):
        response = self.client.get(reverse('dngsmgmt:health'))
        self.assertEqual(response.status_code, 200)
