from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.core import mail

import json
import re

# Create your tests here.
class NopassTestCase(TestCase):
    def post_json(self,url,_dict):
        self.client.post(url,json.dumps(_dict),content_type="application/json")
    def test_user_flow(self):
        User = get_user_model()

        # create an anonymous user
        self.client.get(reverse("nopass_create"))
        self.assertEqual(User.objects.count(),1)
        user = User.objects.all()[0]
        self.assertEqual(user.username+"@example.com",user.email)

        # set user's email to something else
        data = {"email": "arst@asrt.com"}
        self.post_json(reverse("nopass_change_email"),data)
        self.assertEqual(User.objects.all()[0].email,data['email'])

        # get login link
        self.post_json(reverse("nopass_send"),data)
        self.assertEqual(len(mail.outbox),1)

        # login with url
        self.client.logout()
        self.assertTrue('_auth_user_id' not in self.client.session)
        body = mail.outbox[0].body
        url = body.split("http://example.com")[-1].split('\n')[0]
        response = self.client.get(url)
        self.assertEqual(self.client.session['_auth_user_id'],'1')

    def test_bad_token(self):
        redirect = self.client.get(reverse("nopass_login",args=['a','b']))
        self.assertTrue(redirect.url.endswith("bad_token/"))