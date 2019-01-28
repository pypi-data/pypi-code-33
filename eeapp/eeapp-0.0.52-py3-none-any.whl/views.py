# Create your views here.
try:
    from eeapp.rest.view.authView import UserAuthView
except:
    from rest.view.authView import UserAuthView


class AccountAuthView(UserAuthView):
    authModel = None