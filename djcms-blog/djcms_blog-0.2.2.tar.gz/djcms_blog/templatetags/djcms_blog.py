from django import template
from djcms_blog.models import Blog
from django.core.urlresolvers import reverse
from djcms_blog import settings
from django.utils import translation


register = template.Library()


@register.simple_tag(name="blog_url")
def get_blog_url():
    blog = Blog.objects.first()
    if blog:
        return reverse("blog-main", kwargs={"blog_slug": blog.slug})
    return settings.DEFAULT_URL


@register.simple_tag(name="blog_title")
def get_blog_title():
    return settings.BLOG_TITLE


@register.simple_tag(name="blog_root_title")
def get_blog_root_title():
    return settings.ROOT_TITLE


@register.simple_tag(name="blog_navbar_image")
def get_blog_navbar_image():
    return settings.DEFAULT_NAVBAR_IMAGE


@register.simple_tag(name="blog_default_cover_image")
def get_blog_default_cover_image():
    return settings.DEFAULT_COVER_IMAGE


@register.simple_tag(name="blog_markdown_code_css_theme")
def get_blog_markdown_code_css_theme():
    return settings.MARKDOWN_CODE_CSS_THEME
