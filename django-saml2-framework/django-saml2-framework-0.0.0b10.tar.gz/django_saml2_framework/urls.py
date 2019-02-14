# from django.urls import url as path
from django.conf.urls import url

from .views import IdpSsoView, IdpLoginView, IdpLogoutView, IdpMetadataView, SpMetadataView, SpAcsView, SpLoginView, SpLogoutView, IdpSloView, SpSloView

urlpatterns = [
    # default
    url(r'^idp/$', IdpMetadataView.as_view(), name='idp'),
    url(r'^idp/sso$', IdpSsoView.as_view(), name='idp_sso'),
    url(r'^idp/slo$', IdpSloView.as_view(), name='idp_slo'),
    url(r'^idp/login$', IdpLoginView.as_view(), name='idp_login'),
    url(r'^idp/logout$', IdpLogoutView.as_view(), name='idp_logout'),
    # not default
    # path('idp/<entity_id>/', IdpMetadataView.as_view(), name='idp'),
    # path('idp/<entity_id>/sso', IdpSsoView.as_view(), name='idp_sso'),
    # path('idp/<entity_id>/slo', IdpSloView.as_view(), name='idp_slo'),
    # path('idp/<entity_id>/login', IdpLoginView.as_view(), name='idp_login'),
    # path('idp/<entity_id>/logout', IdpLogoutView.as_view(), name='idp_logout'),
    url(r'^idp/(?P<entity_id>.*)/$', IdpMetadataView.as_view(), name='idp'),
    url(r'^idp/(?P<entity_id>.*)/sso$', IdpSsoView.as_view(), name='idp_sso'),
    url(r'^idp/(?P<entity_id>.*)/slo$', IdpSloView.as_view(), name='idp_slo'),
    url(r'^idp/(?P<entity_id>.*)/login$', IdpLoginView.as_view(), name='idp_login'),
    url(r'^idp/(?P<entity_id>.*)/logout$', IdpLogoutView.as_view(), name='idp_logout'),

    # default
    url(r'^sp/$', SpMetadataView.as_view(), name='sp'),
    url(r'^sp/acs$', SpAcsView.as_view(), name='sp_acs'),
    url(r'^sp/slo$', SpSloView.as_view(), name='sp_slo'),
    url(r'^sp/login$', SpLoginView.as_view(), name='sp_login'),
    url(r'^sp/logout$', SpLogoutView.as_view(), name='sp_logout'),
    # not default
    url(r'^sp/(?P<entity_id>.*)/$', SpMetadataView.as_view(), name='sp'),
    url(r'^sp/(?P<entity_id>.*)/acs$', SpAcsView.as_view(), name='sp_acs'),
    url(r'^sp/(?P<entity_id>.*)/slo$', SpSloView.as_view(), name='sp_slo'),
    url(r'^sp/(?P<entity_id>.*)/login$', SpLoginView.as_view(), name='sp_login'),
    url(r'^sp/(?P<entity_id>.*)/logout$', SpLogoutView.as_view(), name='sp_logout'),

    # EXAMPLES
    # path('bio/<username>/', views.bio, name='bio'),
    # path('articles/<slug:title>/', views.article, name='article-detail'),
    # path('articles/<slug:title>/<int:section>/', views.section, name='article-section'),
    # path('weblog/', include('blog.urls')),
]
