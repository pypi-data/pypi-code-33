from django.conf.urls import url

from ccc.click_to_call.views import (AutoDialNumberListView,
                                     AutoDialNumberView, ContactDialView,
                                     DialCallBackView, DialPageView,
                                     OptionPageView, ProcessUploadedFileView,
                                     SaveUploadedListView, UploadedListView,
                                     UploadListOutputView, UploadListView,
                                     call, get_token, uploaded_file_status)

urlpatterns = [
    # URLs for searching for and purchasing a new Twilio number
    url(r'^token$', get_token, name='token'),
    url(r'^call/$', call, name='call'),
    url(r'^options/$', OptionPageView.as_view(), name='call_options_page'),

    url(r'^uploaded-list/(?P<master_list_id>\d+)/$', DialPageView.as_view(), name='dial_form'),

    url(r'^dial/$', DialPageView.as_view(), name='dial_number'),
    url(r'^dial/contacts$', ContactDialView.as_view(), name='dial_contact'),

    url(r'^uploaded-list/$', UploadedListView.as_view(), name='uploaded_list'),

    url(r'^dial_list/$', AutoDialNumberListView.as_view(), name='dial_form'),
    url(r'^dial/(?P<dailer_list_id>\d+)/$', AutoDialNumberView.as_view(), name='dial_list_id'),

    url(r'^upload/$', UploadListView.as_view(), name='upload_excel'),

    url(r'^upload/(?P<master_list_id>\d+)/$', UploadListOutputView.as_view(), name='output_upload_excel'),

    url(r'^submit-excel/$', SaveUploadedListView.as_view(), name='submit_excel'),
    url(r'^process-excel/(?P<master_list_id>\d+)/file/(?P<task_id>[0-9A-Fa-f-]+)$', ProcessUploadedFileView.as_view(),
        name='process_excel'),

    url(r'^process-excel/file/(?P<task_id>[0-9A-Fa-f-]+)/status/$', uploaded_file_status,
        name='process_excel_status'),

    url(r'^update_call_status/(?P<twilio_number>[0-9\+]+)/$', DialCallBackView.as_view(), name='dial_callback'),
]
