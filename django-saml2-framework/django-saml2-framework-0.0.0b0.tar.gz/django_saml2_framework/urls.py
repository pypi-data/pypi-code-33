from django.urls import include, path

from .views import IdpSsoView, IdpLoginView, IdpLogoutView, IdpMetadataView, SpMetadataView, SpAcsView, SpLoginView, SpLogoutView, IdpSloView, SpSloView

urlpatterns = [
    # default
    path('idp/', IdpMetadataView.as_view(), name='idp'),
    path('idp/sso', IdpSsoView.as_view(), name='idp_sso'),
    path('idp/slo', IdpSloView.as_view(), name='idp_slo'),
    path('idp/login', IdpLoginView.as_view(), name='idp_login'),
    path('idp/logout', IdpLogoutView.as_view(), name='idp_logout'),
    # not default
    path('idp/<entity_id>/', IdpMetadataView.as_view(), name='idp'),
    path('idp/<entity_id>/sso', IdpSsoView.as_view(), name='idp_sso'),
    path('idp/<entity_id>/slo', IdpSloView.as_view(), name='idp_slo'),
    path('idp/<entity_id>/login', IdpLoginView.as_view(), name='idp_login'),
    path('idp/<entity_id>/logout', IdpLogoutView.as_view(), name='idp_logout'),


    # default
    path('sp/', SpMetadataView.as_view(), name='sp'),
    path('sp/acs', SpAcsView.as_view(), name='sp_acs'),
    path('sp/slo', SpSloView.as_view(), name='sp_slo'),
    path('sp/login', SpLoginView.as_view(), name='sp_login'),
    path('sp/logout', SpLogoutView.as_view(), name='sp_logout'),
    # not default
    path('sp/<entity_id>/', SpMetadataView.as_view(), name='sp'),
    path('sp/<entity_id>/acs', SpAcsView.as_view(), name='sp_acs'),
    path('sp/<entity_id>/slo', SpSloView.as_view(), name='sp_slo'),
    path('sp/<entity_id>/login', SpLoginView.as_view(), name='sp_login'),
    path('sp/<entity_id>/logout', SpLogoutView.as_view(), name='sp_logout'),

    # EXAMPLES
    # path('bio/<username>/', views.bio, name='bio'),
    # path('articles/<slug:title>/', views.article, name='article-detail'),
    # path('articles/<slug:title>/<int:section>/', views.section, name='article-section'),
    # path('weblog/', include('blog.urls')),
]
