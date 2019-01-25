from django.urls import reverse
from django.test import TestCase
from django.contrib.auth.models import User

from rest_framework.test import APIClient
from .create_data_project import create_projects


class ProjectResponseTestCase(TestCase):

    def setUp(self):
        self.client = APIClient()
        create_projects()
        self.user1 = User.objects.get(username='user1')
        self.user2 = User.objects.get(username='user2')
        self.user3 = User.objects.get(username='user3')
        self.user4 = User.objects.get(username='user4')
        self.user5 = User.objects.get(username='user5')

    def test_project_list(self):
        response = self.client.get(reverse('dngsmgmt:project-list'), format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)
        for o in response.json():
            self.assertEqual(o['name'], 'Public project')

    def test_project_list_user1(self):
        self.client.force_authenticate(self.user1)
        response = self.client.get(reverse('dngsmgmt:project-list'), format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 4)
        count = 0
        for o in response.json():
            if o['name'] == 'Public project' or \
                    o['name'] == 'User1 owner project' or \
                    o['name'] == 'User2 owner project' or \
                    o['name'] == 'User4 owner project':
                count += 1
        self.assertEqual(count, 4)

    def test_project_list_user1_Project1(self):
        self.client.force_authenticate(self.user1)
        response = self.client.get(reverse('dngsmgmt:project-list'),
                                   {'id': 1}, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)
        for o in response.json():
            self.assertEqual(o['name'], 'User1 owner project')

    def test_project_list_user1_Project4(self):
        self.client.force_authenticate(self.user1)
        response = self.client.get(reverse('dngsmgmt:project-list'),
                                   {'id': 4}, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)
        for o in response.json():
            self.assertEqual(o['name'], 'User4 owner project')

    def test_project_list_user1_Project54(self):
        self.client.force_authenticate(self.user1)
        response = self.client.get(reverse('dngsmgmt:project-list'),
                                   {'id': 5}, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)
        for o in response.json():
            self.assertEqual(o['name'], 'Public project')

    def test_project_list_user2_Project1(self):
        self.client.force_authenticate(self.user2)
        response = self.client.get(reverse('dngsmgmt:project-list'),
                                   {'id': 1}, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 0)

    def test_project_list_user2(self):
        self.client.force_authenticate(self.user2)
        response = self.client.get(reverse('dngsmgmt:project-list'), format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 3)
        count = 0
        for o in response.json():
            if o['name'] == 'Public project' or \
                    o['name'] == 'User2 owner project' or \
                    o['name'] == 'User4 owner project':
                count += 1
        self.assertEqual(count, 3)

    def test_project_list_user3(self):
        self.client.force_authenticate(self.user3)
        response = self.client.get(reverse('dngsmgmt:project-list'), format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 3)
        count = 0
        for o in response.json():
            if o['name'] == 'Public project' or \
                    o['name'] == 'User3 owner project' or \
                    o['name'] == 'User4 owner project':
                count += 1
        self.assertEqual(count, 3)

    def test_project_list_user4(self):
        self.client.force_authenticate(self.user4)
        response = self.client.get(reverse('dngsmgmt:project-list'), format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 3)
        count = 0
        for o in response.json():
            if o['name'] == 'Public project' or \
                    o['name'] == 'User3 owner project' or \
                    o['name'] == 'User4 owner project':
                count += 1
        self.assertEqual(count, 3)

    def test_project_list_user5(self):
        self.client.force_authenticate(self.user5)
        response = self.client.get(reverse('dngsmgmt:project-list'), format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)
        count = 0
        for o in response.json():
            if o['name'] == 'Public project':
                count += 1
        self.assertEqual(count, 1)

    def test_project_metadata_list(self):
        self.client.force_authenticate(self.user1)
        response = self.client.get(reverse('dngsmgmt:projectmetadata-list'), format='json')
        self.assertEqual(response.status_code, 403)

    def test_project_metadata_list_user1(self):
        self.client.force_authenticate(self.user1)
        response = self.client.get(reverse('dngsmgmt:projectmetadata-list'),
                                   {'project': '1'}, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 2)
        for o in response.json():
            if o['key'] == 'institution':
                self.assertEqual(o['value'], 'NCBI')
            if o['key'] == 'source':
                self.assertEqual(o['value'], 'human')

    def test_project_metadata_list_user2(self):
        self.client.force_authenticate(self.user2)
        response = self.client.get(reverse('dngsmgmt:projectmetadata-list'),
                                   {'project': '2'}, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 2)
        for o in response.json():
            if o['key'] == 'institution':
                self.assertEqual(o['value'], 'UCSC')
            if o['key'] == 'source':
                self.assertEqual(o['value'], 'fly')

    def test_project_metadata_list_user3(self):
        self.client.force_authenticate(self.user3)
        response = self.client.get(reverse('dngsmgmt:projectmetadata-list'),
                                   {'project': '3'}, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 2)
        for o in response.json():
            if o['key'] == 'institution':
                self.assertEqual(o['value'], 'UM')
            if o['key'] == 'source':
                self.assertEqual(o['value'], 'physalis')

    def test_project_metadata_list_user4(self):
        self.client.force_authenticate(self.user4)
        response = self.client.get(reverse('dngsmgmt:projectmetadata-list'),
                                   {'project': '4'}, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 2)
        for o in response.json():
            if o['key'] == 'institution':
                self.assertEqual(o['value'], 'NCI')
            if o['key'] == 'source':
                self.assertEqual(o['value'], 'banana')

    def test_project_metadata_list_user5(self):
        self.client.force_authenticate(self.user5)
        response = self.client.get(reverse('dngsmgmt:projectmetadata-list'),
                                   {'project': '5'}, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 2)
        for o in response.json():
            if o['key'] == 'institution':
                self.assertEqual(o['value'], 'NIH')
            if o['key'] == 'source':
                self.assertEqual(o['value'], 'mouse')
