from django.contrib.auth.models import User, AnonymousUser
from django.http import HttpResponse

from apps.client.dependency_container import DependencyContainer


class RemoteAuthMiddleware:
    def __init__(self, get_response, aaa_dependency=None):
        self.get_response = get_response

        if aaa_dependency is None:
            self.aaa_dependency = DependencyContainer.aaa
        else:
            self.aaa_dependency = aaa_dependency

    def __call__(self, request):
        if request.path != '/graphql/':
            return self.get_response(request)

        if hasattr(request, 'user') and isinstance(request.user, AnonymousUser):
            return self.get_response(request)

        token = request.META.get('HTTP_AUTHORIZATION')

        if token:
            user = self.aaa_dependency.get_user(token)

            if isinstance(user, User):
                request.user = user
                return self.get_response(request)

        return HttpResponse(status=401)