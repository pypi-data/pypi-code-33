from django.urls import reverse
from django.test import TestCase
from django.contrib.auth.models import User

from rest_framework.test import APIClient
from .create_data_experiment import create_experiments


class ExperimentResponseTestCase(TestCase):

    def setUp(self):
        self.client = APIClient()
        create_experiments()
        self.user1 = User.objects.get(username='user1')
        self.user2 = User.objects.get(username='user2')
        self.user3 = User.objects.get(username='user3')
        self.user4 = User.objects.get(username='user4')
        self.user5 = User.objects.get(username='user5')

    def test_experiment_list(self):
        response = self.client.get(reverse('dngsmgmt:experiment-list'), format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)
        for o in response.json():
            self.assertEqual(o['name'], 'Experiment4')

    def test_experiment_list_user1(self):
        self.client.force_authenticate(self.user1)
        response = self.client.get(reverse('dngsmgmt:experiment-list'), format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 3)
        count = 0
        for o in response.json():
            if o['name'] == 'Experiment1' or \
                    o['name'] == 'Experiment2' or \
                    o['name'] == 'Experiment4':
                count += 1
        self.assertEqual(count, 3)

    def test_experiment_metadata_list(self):
        self.client.force_authenticate(self.user1)
        response = self.client.get(reverse('dngsmgmt:experimentmetadata-list'), format='json')
        self.assertEqual(response.status_code, 403)

    def test_experiment_metadata_list_user1(self):
        self.client.force_authenticate(self.user1)
        response = self.client.get(reverse('dngsmgmt:experimentmetadata-list'),
                                   {'experiment': '1'}, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 2)
        for o in response.json():
            if o['key'] == 'tissue':
                self.assertEqual(o['value'], 'Lung cancer')
            if o['key'] == 'cell':
                self.assertEqual(o['value'], 'H69AR')

    def test_experiment_list_user2(self):
        self.client.force_authenticate(self.user2)
        response = self.client.get(reverse('dngsmgmt:experiment-list'), format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 2)
        count = 0
        for o in response.json():
            if o['name'] == 'Experiment2' or \
                    o['name'] == 'Experiment4':
                count += 1
        self.assertEqual(count, 2)

    def test_experiment_metadata_list_user2_experiment1(self):
        self.client.force_authenticate(self.user2)
        response = self.client.get(reverse('dngsmgmt:experimentmetadata-list'),
                                   {'experiment': '1'}, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 0)

    def test_experiment_metadata_list_user2_experiment2(self):
        self.client.force_authenticate(self.user2)
        response = self.client.get(reverse('dngsmgmt:experimentmetadata-list'),
                                   {'experiment': '2'}, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 2)
        for o in response.json():
            if o['key'] == 'tissue':
                self.assertEqual(o['value'], 'Lung cancer')
            if o['key'] == 'cell':
                self.assertEqual(o['value'], 'H69AR')

    def test_experiment_list_user3(self):
        self.client.force_authenticate(self.user3)
        response = self.client.get(reverse('dngsmgmt:experiment-list'), format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 2)
        count = 0
        for o in response.json():
            if o['name'] == 'Experiment3' or \
                    o['name'] == 'Experiment4':
                count += 1
        self.assertEqual(count, 2)

    def test_experiment_metadata_list_user3_experiment3(self):
        self.client.force_authenticate(self.user3)
        response = self.client.get(reverse('dngsmgmt:experimentmetadata-list'),
                                   {'experiment': '3'}, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 2)
        for o in response.json():
            if o['key'] == 'tissue':
                self.assertEqual(o['value'], 'Lung cancer')
            if o['key'] == 'cell':
                self.assertEqual(o['value'], 'H69AR')
