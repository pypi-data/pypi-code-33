from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth.models import Group

from ..models import Consumer


class ComsumersTests(APITestCase):
    def setUp(self):
        self.staff_consumer_id = 'a1-a1'
        self.staff_consumer = Consumer.objects.create_user(self.staff_consumer_id, is_staff=True)

        self.custom_consumer_id = 'b1-b1'
        self.custom_consumer = Consumer.objects.create_user(self.custom_consumer_id)


    def test_create_consumer(self):
        """
        Ensure we can create a new consumer object.
        """
        url = reverse('consumer-list')

        kong_consumer_id = 'b2-b2'
        group = 'example.com'

        headers = {
            'HTTP_X_CONSUMER_USERNAME': kong_consumer_id,
            'HTTP_X_CONSUMER_GROUPS': group
        }

        response = self.client.get(url, **headers, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(Consumer.objects.count(), 3)
        self.assertEqual(Consumer.objects.filter(kong_consumer_id=kong_consumer_id).count(), 1)
        self.assertEqual(Group.objects.filter(name=group).count(), 1)


    def test_create_staff_consumer(self):
        """
        Ensure we can create a new staff consumer object.
        """
        url = reverse('consumer-list')

        kong_consumer_id = 'a2-a2'
        group = 'staff'

        headers = {
            'HTTP_X_CONSUMER_USERNAME': kong_consumer_id,
            'HTTP_X_CONSUMER_GROUPS': group
        }

        response = self.client.get(url, **headers, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(Consumer.objects.count(), 3)
        self.assertEqual(Consumer.objects.filter(kong_consumer_id=kong_consumer_id).count(), 1)
        self.assertEqual(Group.objects.filter(name=group).count(), 0)


    def test_staff_consumer_can_list_all_users(self):
        """
        Ensure we can create a new staff consumer object.
        """
        url = reverse('consumer-list')

        kong_consumer_id = 'a2-a2'
        group = 'staff'

        headers = {
            'HTTP_X_CONSUMER_USERNAME': kong_consumer_id,
            'HTTP_X_CONSUMER_GROUPS': group
        }

        response = self.client.get(url, **headers, format='json')
        response_data = response.json()
        self.assertEqual(len(response_data), 3)


    def test_custom_consumer_can_list_only_self(self):
        """
        Ensure we can create a new staff consumer object.
        """
        url = reverse('consumer-list')

        kong_consumer_id = 'b2-b2'
        group = 'example.com'

        headers = {
            'HTTP_X_CONSUMER_USERNAME': kong_consumer_id,
            'HTTP_X_CONSUMER_GROUPS': group
        }

        response = self.client.get(url, **headers, format='json')
        response_data = response.json()
        self.assertEqual(len(response_data), 1)


    def test_custom_consumer_can_get_only_self(self):
        """
        Ensure we can create a new staff consumer object.
        """

        kong_consumer_id = 'b2-b2'
        group = 'example.com'

        headers = {
            'HTTP_X_CONSUMER_USERNAME': kong_consumer_id,
            'HTTP_X_CONSUMER_GROUPS': group
        }

        url = reverse('consumer-detail', args=(kong_consumer_id, ))

        response = self.client.get(url, **headers, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response_data = response.json()
        self.assertEqual(response_data.get('kong_consumer_id'), kong_consumer_id)

        url2 = reverse('consumer-detail', args=(self.custom_consumer_id, ))

        response2 = self.client.get(url2, **headers, format='json')
        self.assertEqual(response2.status_code, status.HTTP_404_NOT_FOUND)


    def test_staff_consumer_can_get_different_user(self):
        """
        Ensure we can create a new staff consumer object.
        """

        kong_consumer_id = 'a2-a2'
        group = 'staff'

        headers = {
            'HTTP_X_CONSUMER_USERNAME': kong_consumer_id,
            'HTTP_X_CONSUMER_GROUPS': group
        }

        url = reverse('consumer-detail', args=(kong_consumer_id, ))

        response = self.client.get(url, **headers, format='json')
        response_data = response.json()
        self.assertEqual(response_data.get('kong_consumer_id'), kong_consumer_id)

        url2 = reverse('consumer-detail', args=(self.custom_consumer_id, ))

        response2 = self.client.get(url2, **headers, format='json')
        self.assertEqual(response2.status_code, status.HTTP_200_OK)

        response2_data = response2.json()
        self.assertEqual(response2_data.get('kong_consumer_id'), self.custom_consumer_id)


    def test_can_update_groups(self):
        """
        Ensure we can create a new staff consumer object.
        """

        kong_consumer_id = 'b2-b2'
        group = 'example.com'

        headers = {
            'HTTP_X_CONSUMER_USERNAME': kong_consumer_id,
            'HTTP_X_CONSUMER_GROUPS': group
        }

        url = reverse('consumer-detail', args=(kong_consumer_id, ))

        response = self.client.get(url, **headers, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response_data = response.json()
        self.assertEqual(response_data.get('kong_consumer_id'), kong_consumer_id)

        group2 = 'example.org, staff'
        headers2 = {
            'HTTP_X_CONSUMER_USERNAME': kong_consumer_id,
            'HTTP_X_CONSUMER_GROUPS': group2
        }

        url2 = reverse('consumer-detail', args=(kong_consumer_id, ))

        response2 = self.client.get(url2, **headers2, format='json')
        self.assertEqual(response2.status_code, status.HTTP_200_OK)

        self.assertEqual(Consumer.objects.get(kong_consumer_id=kong_consumer_id).is_staff, True)
        self.assertEqual(Consumer.objects.get(kong_consumer_id=kong_consumer_id).groups.count(), 1)
        self.assertEqual(Consumer.objects.get(kong_consumer_id=kong_consumer_id).groups.filter(name=group).count(), 0)
        self.assertEqual(Consumer.objects.get(kong_consumer_id=kong_consumer_id).groups.filter(name='example.org').count(), 1)
