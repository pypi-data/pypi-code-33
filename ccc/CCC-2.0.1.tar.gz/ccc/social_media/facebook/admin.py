# Register your models here.
from django.contrib import admin

from ccc.social_media.facebook.models import (AccessToken, AuthState,
                                              FacebookProfile)

admin.site.register(AuthState)
admin.site.register(AccessToken)
admin.site.register(FacebookProfile)
