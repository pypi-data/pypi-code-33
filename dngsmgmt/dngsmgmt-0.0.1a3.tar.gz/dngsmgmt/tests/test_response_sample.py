from django.urls import reverse
from django.test import TestCase
from django.contrib.auth.models import User

from rest_framework.test import APIClient
from .create_data_sample import create_samples


class SampleResponseTestCase(TestCase):

    def setUp(self):
        self.client = APIClient()
        create_samples()
        self.user1 = User.objects.get(username='user1')
        self.user2 = User.objects.get(username='user2')
        self.user3 = User.objects.get(username='user3')
        self.user4 = User.objects.get(username='user4')

    def test_sample_list(self):
        response = self.client.get(reverse('dngsmgmt:sample-list'), format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)
        for o in response.json():
            self.assertEqual(o['name'], 'Sample1')

    def test_sample_list_user1(self):
        self.client.force_authenticate(self.user1)
        response = self.client.get(reverse('dngsmgmt:sample-list'), format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 3)
        count = 0
        for o in response.json():
            if o['name'] == 'Sample1' or \
                    o['name'] == 'Sample2' or \
                    o['name'] == 'Sample3':
                count += 1
        self.assertEqual(count, 3)

    def test_sample_metadata_list(self):
        self.client.force_authenticate(self.user1)
        response = self.client.get(reverse('dngsmgmt:samplemetadata-list'), format='json')
        self.assertEqual(response.status_code, 403)

    def test_sample_metadata_list_user1(self):
        self.client.force_authenticate(self.user1)
        response = self.client.get(reverse('dngsmgmt:samplemetadata-list'),
                                   {'sample': '1'}, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 2)
        for o in response.json():
            if o['key'] == 'tissue':
                self.assertEqual(o['value'], 'Lung cancer')
            if o['key'] == 'cell':
                self.assertEqual(o['value'], 'H69AR')

    def test_sample_list_user2(self):
        self.client.force_authenticate(self.user2)
        response = self.client.get(reverse('dngsmgmt:sample-list'), format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 3)
        count = 0
        for o in response.json():
            if o['name'] == 'Sample1' or \
                    o['name'] == 'Sample2' or \
                    o['name'] == 'Sample3':
                count += 1
        self.assertEqual(count, 3)

    def test_sample_metadata_list_user2_sample2(self):
        self.client.force_authenticate(self.user2)
        response = self.client.get(reverse('dngsmgmt:samplemetadata-list'),
                                   {'sample': '1'}, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 2)
        for o in response.json():
            if o['key'] == 'tissue':
                self.assertEqual(o['value'], 'Lung cancer')
            if o['key'] == 'cell':
                self.assertEqual(o['value'], 'H69AR')

    def test_sample_list_user3(self):
        self.client.force_authenticate(self.user3)
        response = self.client.get(reverse('dngsmgmt:sample-list'), format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 2)
        count = 0
        for o in response.json():
            if o['name'] == 'Sample1' or \
                    o['name'] == 'Sample4':
                count += 1
        self.assertEqual(count, 2)

    def test_sample_metadata_list_user3_sample4(self):
        self.client.force_authenticate(self.user3)
        response = self.client.get(reverse('dngsmgmt:samplemetadata-list'),
                                   {'sample': '4'}, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 2)
        for o in response.json():
            if o['key'] == 'tissue':
                self.assertEqual(o['value'], 'Lung cancer')
            if o['key'] == 'cell':
                self.assertEqual(o['value'], 'H69AR')
