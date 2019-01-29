from django.urls import path

from ccc.contacts import views

app_name = 'contacts'

urlpatterns = [
    path('', views.ContactsList.as_view(), name='contacts_list'),
    path('groups/', views.ContactsGroupsList.as_view(), name='contact_groups_list'),
]
