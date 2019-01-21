from django.urls import include, path

urlpatterns = [
    path('tests/', include('tests.urls')),
]
