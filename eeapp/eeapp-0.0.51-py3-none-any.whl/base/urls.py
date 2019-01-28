from rest_framework.routers import DefaultRouter,SimpleRouter
from django.conf.urls import url,include


from .views import AccountAuthView
# router1 = SimpleRouter(trailing_slash=False)

router = DefaultRouter(trailing_slash=False)
router.register('auth',AccountAuthView,'auth')

urlpatterns = [
    url(r'^',include(router.urls)),
]

from rest_framework.authtoken import views
# urlpatterns += [
#     url(r'^api-auth', MemberTokenAuthView.as_view())
# ]