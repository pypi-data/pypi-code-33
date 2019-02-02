from django.http import JsonResponse, HttpResponseRedirect, HttpResponse
from django.contrib.auth import login, get_user_model
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.tokens import default_token_generator
from django.core.exceptions import ValidationError
from django.urls import reverse
from django.utils.http import urlsafe_base64_decode

import json
import random


def bad_token(request):
    message = "The link you are using is invalid or expired. Please try again."
    return HttpResponse("<h1>Bad Token</h1><p>{}</p>".format(message))


def create(request):
    data = json.loads(request.body.decode("utf-8") or "{}")
    username = email = data.get("email",None)
    User = get_user_model()
    if email and User.objects.filter(email=email):
        raise NotImplemented()
    while not username or User.objects.filter(username=username):
        _hash = "{:032x}".format(random.getrandbits(128))
        username = "guest-{}".format(_hash[:8])
        email = username + "@example.com"
    user = User.objects.create(
        username=username,
        email=email
    )
    user.backend = "django.contrib.auth.backends.ModelBackend"
    login(request,user)
    return JsonResponse({"status": "ok"})


def change_email(request):
    data = json.loads(request.body.decode("utf-8"))
    email = data.get("email",None)
    User = get_user_model()
    user = request.user
    if User.objects.exclude(id=user.id).filter(email=email):
        return JsonResponse(
            {'error': 'Another account already has that email.'},
            status=400
        )
    user = request.user
    user.email = user.username = email
    user.save()
    return JsonResponse({"success": "Email address updated"})


def send(request):
    data = json.loads(request.body.decode("utf-8"))
    form = PasswordResetForm(data)
    if form.is_valid():
        form.save(
            subject_template_name='email/nopass/subject.txt',
            email_template_name='email/nopass/body.txt',
        )
        return JsonResponse({"success":"Please check your email for a login link."})
    return JsonResponse({},status=400)


# django.contrib.auth.views.PasswordResetConfirmView.get_user
def get_user(uidb64):
    User = get_user_model()
    try:
        # urlsafe_base64_decode() decodes to bytestring
        uid = urlsafe_base64_decode(uidb64).decode()
        return User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist, ValidationError):
        return None


# adapted from django.contrib.auth.views.PasswordResetConfirmView
def complete_login(request, uidb64=None, token=None):
    redirect_url = '/'
    if request.user.is_authenticated:
        return HttpResponseRedirect(redirect_url)
    user = get_user(uidb64)

    if user and default_token_generator.check_token(user, token):
        # log the user and redirect to change password
        # logging in invalidates the token
        user.backend = "django.contrib.auth.backends.ModelBackend"
        login(request, user)

        # this forces them to change password
        user.set_unusable_password()
    else:
        redirect_url = reverse("nopass_bad_token")
    return HttpResponseRedirect(redirect_url)