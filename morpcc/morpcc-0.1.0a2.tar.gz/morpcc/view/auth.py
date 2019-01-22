from morpfw.authn.pas.user.path import get_user_collection
import morepath
from ..app import App
from ..app import SQLAuthApp
from ..root import Root
import html
import urllib.parse


@App.html(model=Root, name='login', template='master/login.pt')
def login(context, request):
    pass


@App.html(model=Root, name='login', template='master/login.pt', request_method='POST')
def process_login(context, request):
    username = request.POST.get('username')
    password = request.POST.get('password')
    newreq = request.copy(app=SQLAuthApp())
    collection = get_user_collection(newreq)

    if not collection.authenticate(username, password):
        request.notify('error', 'Invalid Login',
                       'Please check your username / password')
        return

    @request.after
    def remember(response):
        """Remember the identity of the user logged in."""
        # We pass the extra info to the identity object.
        response.headers.add('Access-Control-Expose-Headers', 'Authorization')
        u = collection.get(username)
        identity = morepath.Identity(u.userid)
        request.app.remember_identity(response, request, identity)
    came_from = request.GET.get('came_from', '')
    if came_from:
        came_from = urllib.parse.unquote(came_from)
    else:
        came_from = request.relative_url('/')
    return morepath.redirect(came_from)


@App.view(model=Root, name='logout')
def logout(context, request):
    @request.after
    def forget(response):
        request.app.forget_identity(response, request)

    return morepath.redirect(request.relative_url('/'))
