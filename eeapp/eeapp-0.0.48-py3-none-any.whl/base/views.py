from django.shortcuts import render

# Create your views here.
try:
    from ..rest.view.authView import UserAuthView
except:
    from rest.view.authView import UserAuthView


from .models import Account,SuperAccount
class AccountAuthView(UserAuthView):
    authModel = SuperAccount