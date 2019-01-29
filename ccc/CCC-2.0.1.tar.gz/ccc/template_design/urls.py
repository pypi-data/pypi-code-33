from django.conf.urls import url

from ccc.template_design.views import (EmailAndWebAnalyticsView,
                                       MyPageTemplateView,
                                       TemplateDesignDeleteView,
                                       TemplateDesignFormView,
                                       TemplateDesignListView,
                                       WebTemplateDesignFormView)

app_name = 'template-design'

urlpatterns = [
    url(r'^design/(?P<pk>[0-9]+)/email/$', TemplateDesignFormView.as_view(), name='design_template_email_update'),
    url(r'^design/(?P<pk>[0-9]+)/web/$', WebTemplateDesignFormView.as_view(), name='design_template_web_update'),
    url(r'^design/(?P<pk>[0-9]+)/delete/$', TemplateDesignDeleteView.as_view(), name='design_template_delete'),
    url(r'^mypage/(?P<pk>[0-9]+)/(?P<name_slug>[\w-]+)/$', MyPageTemplateView.as_view(), name='design_my_page'),
    url(r'^web/$', WebTemplateDesignFormView.as_view(), name='design_web'),
    url(r'^email/$', TemplateDesignFormView.as_view(), name='design_email'),
    url(r'^landingpage/$', TemplateDesignListView.as_view(), name='design_landing_page'),
    url(r'^emailandwebanalytics/$', EmailAndWebAnalyticsView.as_view(), name='emailandweb_analytics'),
]
