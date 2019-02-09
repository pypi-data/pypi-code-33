from django.contrib import admin

from authentication.models import AuthToken

admin.site.register(AuthToken)
