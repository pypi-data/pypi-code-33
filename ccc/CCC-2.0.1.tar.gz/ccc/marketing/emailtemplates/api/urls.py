from rest_framework.routers import SimpleRouter

from ccc.marketing.emailtemplates.api.views import EmailTemplateViewSet

app_name = 'emailtemplates'

router = SimpleRouter()
router.register(r'', EmailTemplateViewSet, base_name='email_template')

urlpatterns = router.urls
