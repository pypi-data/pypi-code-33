"""
The application provides no URLs of its own.
In development mode, this will include the admin package.
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/doc/', include('django.contrib.admindocs.urls')),
    path('admin/', admin.site.urls),
]
