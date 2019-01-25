from django.conf.urls import url
from functools import wraps
from django.utils.decorators import available_attrs
from django.views.decorators.cache import cache_page
from djcms_blog.settings import DJCMS_BLOG_CACHE_TIME

from . import views


def cache_for_anonim(timeout):
    def decorator(view_func):
        @wraps(view_func, assigned=available_attrs(view_func))
        def _wrapped_view(request, *args, **kwargs):

            if request.user.is_staff:
                return (view_func)(request, *args, **kwargs)
            else:
                return cache_page(timeout)(view_func)(request, *args, **kwargs)

        return _wrapped_view

    return decorator


urlpatterns = [
    url(
        r"^(?P<blog_slug>[\w-]+)/index/$",
        cache_for_anonim(DJCMS_BLOG_CACHE_TIME)(views.BlogView.as_view()),
        name="blog-main",
    ),
    url(
        r"^author/(?P<author_slug>[\w-]+)/$",
        cache_for_anonim(DJCMS_BLOG_CACHE_TIME)(views.AutorView.as_view()),
        name="author-main",
    ),
    url(
        r"^(?P<blog_slug>[\w-]+)/tag/(?P<tag_slug>[\w-]+)/$",
        cache_for_anonim(DJCMS_BLOG_CACHE_TIME)(views.TagView.as_view()),
        name="tag-main",
    ),
    url(
        r"^(?P<blog_slug>[\w-]+)/(?P<post_slug>[\w-]+)/$",
        cache_for_anonim(DJCMS_BLOG_CACHE_TIME)(views.PostView.as_view()),
        name="post-detail",
    ),
    url(
        r"^draft/(?P<blog_slug>[\w-]+)/(?P<post_slug>[\w-]+)/$",
        views.PostDraftView.as_view(),
        name="draft-post-detail",
    ),
]
