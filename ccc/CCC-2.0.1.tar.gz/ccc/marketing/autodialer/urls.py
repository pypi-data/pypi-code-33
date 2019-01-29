from django.urls import path

from ccc.marketing.autodialer import views

app_name = 'autodialer'

urlpatterns = [
    path('dial/', views.DialNumberView.as_view(), name='dial-number'),
    path('dial/contacts/', views.DialContactsView.as_view(), name='dial-contact'),
    path('dial/personalized-messages/', views.PersonalizedMessagesView.as_view(), name='personalized-messages'),
    path('dial/master/', views.DialMasterListView.as_view(), name='master-list'),
    path('dial/master/<int:pk>/', views.DialMasterListDetailView.as_view(), name='master-list-detail'),
    path('dial/master/<int:pk>/status/', views.DialMasterListStatusView.as_view(), name='master-list-status'),
]
