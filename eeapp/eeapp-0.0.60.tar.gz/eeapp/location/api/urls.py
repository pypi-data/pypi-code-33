from rest_framework.routers import DefaultRouter,SimpleRouter
from django.conf.urls import url,include

from .views import *

# router1 = SimpleRouter(trailing_slash=False)

router = DefaultRouter(trailing_slash=False)
router.register('province',ProvinceListView)
router.register('cities',CityListView,base_name='cities')
router.register('areas',AreaListView,base_name='areas')
urlpatterns = [
    url(r'^',include(router.urls)),
]
