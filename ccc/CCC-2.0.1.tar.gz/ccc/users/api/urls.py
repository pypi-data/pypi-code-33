from rest_framework.routers import DefaultRouter

from ccc.users.api import views

app_name = 'api_users'

router = DefaultRouter()
router.register('', views.UserViewSet, base_name='user')

urlpatterns = router.urls
