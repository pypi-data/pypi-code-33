from rest_framework.routers import DefaultRouter,SimpleRouter
from django.conf.urls import url,include

from .views import *

# router1 = SimpleRouter(trailing_slash=False)

router = DefaultRouter(trailing_slash=False)
router.register('image',ImageView,base_name='image')
router.register('test-model',TestModelView,base_name='test'),
router.register('options',OptionsView,base_name='options'),

urlpatterns = router.urls
# urlpatterns = [
#     url(r'^',include(router.urls)),
# ]
