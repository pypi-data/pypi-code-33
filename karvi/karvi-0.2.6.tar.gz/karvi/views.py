from django.conf import settings
from django.contrib.auth import login, authenticate
from django.shortcuts import redirect
from django.views.generic import TemplateView, FormView

from .forms import UserSignupForm


class IndexView(TemplateView):
    template_name = 'karvi/index.html'


class UserCreationView(FormView):
    form_class = UserSignupForm
    template_name = 'registration/signup.html'

    def form_valid(self, form):
        form.save()
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password1')
        user = authenticate(username=username, password=password)
        login(self.request, user)
        return redirect(settings.SIGNUP_REDIRECT_URL)
