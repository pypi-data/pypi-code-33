from django.contrib.auth import login
from django.contrib.auth.models import User
from logging import getLogger
from django_navbar_client.models import AuthProfile

logger = getLogger(__name__)


class CreateAnonymousUser:
    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.
        if request.user.is_anonymous:
            user, found = User.objects.get_or_create(username="anonymous")
            request.user = user

        response = self.get_response(request)

        # Code to be executed for each request/response after
        # the view is called.

        return response


class ParamUUIDUserMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        uuid = request.GET.get("UUID", request.GET.get("uuid", False))
        try:
            if uuid and (request.user.is_anonymous or (
                    request.user.authprofile and request.user.authprofile.uuid != uuid)):
                user = AuthProfile.objects.get(uuid=uuid).user
                if request.user.is_authenticated:
                    logger.info("User override {} Now is {}", request.user.username, user)
                login(request, user, backend='oauth2_provider.backends.OAuth2Backend')
                request.user = request._cached_user = user
        except (AuthProfile.DoesNotExist, ):
            logger.debug("User {} not found", uuid)
        return self.get_response(request)
