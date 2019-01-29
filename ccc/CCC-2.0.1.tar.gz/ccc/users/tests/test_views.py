import json

from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import AnonymousUser
from django.contrib.sessions.middleware import SessionMiddleware
from django.test import Client, RequestFactory, TestCase
from django.test.client import Client
from django.urls import reverse

from ccc.users import views
from ccc.users.views import (ChangePassword, login_authentication, ProfileUpdate, register,
                             home)
from mixer.backend.django import mixer

UserProfile = get_user_model()


class TestSignUpView(TestCase):
    def setUp(self):
        self.get_req = RequestFactory().get('/')
        self.factory = RequestFactory()

    def test_anonymous_access(self):
        """make sure the sign up view doesn't require being signed in"""
        self.get_req.user = AnonymousUser()
        resp = views.register(self.get_req)
        self.assertEqual(resp.status_code, 200, 'This registration view should be accessible anonymously')

    def test_signed_in_user_cannot_access_register(self):
        """test that the user is redirected when they try to access the register page if they are already signed in"""
        user = mixer.blend(UserProfile)
        self.get_req.user = user
        resp = views.register(self.get_req)
        assert resp.status_code == 302, 'Authenticated user should be sent to the home page if they try to access ' \
                                        'registration page'


class TestSignInView(TestCase):
    def setUp(self):
        self.get_req = RequestFactory().get('/')

    def test_anonymous_access(self):
        """make sure the login view doesn't require being signed in"""
        self.get_req.user = AnonymousUser()
        resp = views.login_authentication(self.get_req)
        self.assertEqual(resp.status_code, 200, 'This login view should be accessible anonymously')

    def test_signed_in_user_cannot_access_register(self):
        """test that the user is redirected when they try to access the login page if they are already signed in"""
        user = mixer.blend(UserProfile)
        self.get_req.user = user
        resp = views.login_authentication(self.get_req)
        assert resp.status_code == 302, 'Authenticated user should be sent to the home page if they try to access ' \
                                        'sign in page'


class TestForgotPasswordView(TestCase):
    def setUp(self):
        self.get_req = RequestFactory().get('/')

    def test_access_to_forgot_password_page(self):
        """Make sure that the forgot password page is accessible and returns a 200"""
        self.get_req.user = AnonymousUser()
        resp = views.ResetPasswordView.as_view()(self.get_req)
        self.assertEqual(resp.status_code, 200, 'This forgot password view is working properly')


class TestProfileUpdate(TestCase):

    def setUp(self):
        # self.client = Client()
        self.factory = RequestFactory()

    def test_get_profile_update(self):
        # test req method GET
        user = mixer.blend(UserProfile)
        request = self.factory.get('/user/profile')
        request.user = user
        response = ProfileUpdate.as_view()(request)   # this is the syntax for class-based views.
        self.assertEqual(response.status_code, 200)

    def test_post_profile_update(self):
        # test req method POST with data
        user = mixer.blend(UserProfile)
        form_data = {
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'title': user.title,
        }
        request = self.factory.post('/user/profile', form_data)
        request.user = user
        response = ProfileUpdate.as_view()(request)
        self.assertEqual(response.status_code, 200)


class TestChangePassword(TestCase):

    def setUp(self):
        self.factory = RequestFactory()

    def test_post_change_password_form_invalid(self):
        user = mixer.blend(UserProfile)
        request = self.factory.post('/user/user_password_change', {}) # testing with empty data
        request.user = user
        response = ChangePassword.as_view()(request)
        self.assertEqual(response.status_code, 200)
        exp_data = {
            'status': 'error',
            'result': {
                'old_password': ['This field is required.'],
                'new_password1': ['This field is required.'],
                'new_password2': ['This field is required.']
            }
        }
        self.assertEqual(exp_data, json.loads(response.content))

    def test_post_change_password_form_valid(self):
        # user = mixer.blend(UserProfile, password=make_password('secret'))
        user = mixer.blend(UserProfile, password=make_password('secret'))
        user.set_password('secret')
        req_data = dict(old_password='secret', new_password1='secretly', new_password2='secretly')
        response = self.client.post('/user/user_password_change/', req_data)  # testing with data
        self.assertEqual(response.status_code, 200)
        exp_data = {
            'status': 'success',
            'url': '/user/dashboard'
        }
        self.assertEqual(exp_data, json.loads(response.content))


class TestRegister(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_get_register_page(self):
        request = self.factory.get('/register')   # testing for new users
        request.user = AnonymousUser()
        response = register(request)
        self.assertEqual(response.status_code, 200)


class TestLoginView(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = mixer.blend(UserProfile, password=make_password('secret'))
        self.user2 = mixer.blend(UserProfile, password=make_password('secret'))
        self.user2.is_active = False
        self.user2.save()

    def setup_request(self, request, active):

        if active:
            request.user = self.user
        else:
            request.user = self.user2

        """Annotate a request object with a session"""
        middleware = SessionMiddleware()
        middleware.process_request(request)
        request.session.save()

        request.session['some'] = 'some'
        request.session.save()

    def test_sign_in_with_empty_data(self):
        #user = mixer.blend(UserProfile)
        request = self.factory.post('/user/login/', {})
        self.setup_request(request, True)
        response = login_authentication(request)
        exp_data = dict(success='false', message='login Fail!')
        self.assertEqual(exp_data, json.loads(response.content))

    def test_signin_with_data(self):
        # user = mixer.blend(UserProfile, password=make_password('secret'))
        form_data = dict(password='secret', email=self.user.email)
        request = self.factory.post('/user/login/', form_data)
        self.setup_request(request, True)
        response = login_authentication(request)
        exp_data = dict(success='true')
        self.assertEqual(exp_data, json.loads(response.content))

    def test_signin_with_non_active_user(self):
        # user = mixer.blend(UserProfile, password=make_password('secret'))
        form_data = dict(password='secret', email=self.user2.email)
        request = self.factory.post('/user/login/', form_data)
        self.setup_request(request, False)
        response = login_authentication(request)
        exp_data = dict(success='false', message='Account Is disabled, contact us to resolve this')
        self.assertEqual(exp_data, json.loads(response.content))
