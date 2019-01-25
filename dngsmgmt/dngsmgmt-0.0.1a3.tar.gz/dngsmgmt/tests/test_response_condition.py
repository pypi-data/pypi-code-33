from django.urls import reverse
from django.test import TestCase
from django.contrib.auth.models import User

from rest_framework.test import APIClient
from .create_data_condition import create_conditions


class ConditionResponseTestCase(TestCase):

    def setUp(self):
        self.client = APIClient()
        create_conditions()
        self.user1 = User.objects.get(username='user1')
        self.user2 = User.objects.get(username='user2')
        self.user3 = User.objects.get(username='user3')
        self.user4 = User.objects.get(username='user4')

    def test_condition_list_user1(self):
        self.client.force_authenticate(self.user1)
        response = self.client.get(reverse('dngsmgmt:condition-list'), format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 4)
        count = 0
        for o in response.json():
            if o['name'] == 'Condition1':
                self.assertEqual(len(o['samples']), 1)
                count += 1
            if o['name'] == 'Condition2':
                self.assertEqual(len(o['samples']), 2)
                count += 1
            if o['name'] == 'Condition3':
                self.assertEqual(len(o['samples']), 2)
                count += 1
            if o['name'] == 'Condition4':
                self.assertEqual(len(o['samples']), 1)
                count += 1
        self.assertEqual(count, 4)

    def test_condition_list(self):
        response = self.client.get(reverse('dngsmgmt:condition-list'), format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 2)
        count = 0
        for o in response.json():
            if o['name'] == 'Condition1':
                self.assertEqual(len(o['samples']), 1)
                count += 1
            if o['name'] == 'Condition2':
                self.assertEqual(len(o['samples']), 2)
                count += 1
        self.assertEqual(count, 2)

    def test_condition_in_list(self):
        self.client.force_authenticate(self.user2)
        response = self.client.get(reverse('dngsmgmt:condition-list'),
                                   {'ids': ['3', '4']}, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 2)
        count = 0
        for o in response.json():
            if o['name'] == 'Condition3':
                self.assertEqual(len(o['samples']), 2)
                count += 1
            if o['name'] == 'Condition4':
                self.assertEqual(len(o['samples']), 1)
                count += 1
        self.assertEqual(count, 2)

    def test_condition_list_user4(self):
        self.client.force_authenticate(self.user4)
        response = self.client.get(reverse('dngsmgmt:condition-list'), format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 2)
        count = 0
        for o in response.json():
            if o['name'] == 'Condition1':
                self.assertEqual(len(o['samples']), 1)
                count += 1
            if o['name'] == 'Condition2':
                self.assertEqual(len(o['samples']), 2)
                count += 1
        self.assertEqual(count, 2)

    def test_condition_list_user3(self):
        self.client.force_authenticate(self.user3)
        response = self.client.get(reverse('dngsmgmt:condition-list'), format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 3)
        count = 0
        for o in response.json():
            if o['name'] == 'Condition1':
                self.assertEqual(len(o['samples']), 1)
                count += 1
            if o['name'] == 'Condition2':
                self.assertEqual(len(o['samples']), 2)
                count += 1
            if o['name'] == 'Condition5':
                self.assertEqual(len(o['samples']), 1)
                count += 1
        self.assertEqual(count, 3)
