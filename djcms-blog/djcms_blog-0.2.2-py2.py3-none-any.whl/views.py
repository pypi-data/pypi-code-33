from django.http import Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext as _
from django.views.generic import DetailView
from django.utils import translation
from django.contrib import messages

from djcms_blog import settings
from .models import Author, Blog, Tag, Post, PostTitle


def delete_published_posts(request):
    if request.user.is_superuser:
        PostTitle.objects.filter(is_draft=False, published=True).delete()
        draft_posts = PostTitle.objects.filter(is_draft=True, published=True)
        for post in draft_posts:
            post.published = False
            post.save()
        messages.add_message(request, messages.INFO, 'Posts unpublished.')
    else:
        messages.add_message(request, messages.INFO, 'You can\'t unpublish all posts')
    return HttpResponseRedirect('/admin/djcms_blog/posttitle/')


class BlogDetailView(DetailView):
    language = None

    def get_language_code(self, url_path=None):
        assert url_path, 'Empty url path'
        lang_code = url_path.split("/")[1]
        return lang_code

    def set_language(self):
        self.language = translation.get_language()
        if self.language is None:
            self.language = self.get_language_code(self.request.META["PATH_INFO"])
        if self.language not in (lang[0] for lang in settings.LANGUAGES):
            raise Http404


class BlogView(BlogDetailView):
    template_name = "djcms_blog/blog.html"
    slug_field = "slug"
    slug_url_kwarg = "blog_slug"
    model = Blog
    object = None

    def get_context_data(self, **kwargs):
        context = super(BlogView, self).get_context_data(**kwargs)
        return context

    def get(self, request, *args, **kwargs):
        self.set_language()
        self.object = self.get_object()
        lang_object = self.object.get_language_object(self.language)
        if lang_object is None:
            raise Http404
        self.object.slug = self.object.slug if settings.DEFAULT_BLOG_ID is None else ''
        self.object.description = lang_object.description
        self.object.meta_title = lang_object.meta_title
        self.object.meta_description = lang_object.meta_description
        self.object.get_posts = self.object.get_posts()
        for post in self.object.get_posts:
            post_object = post.language_object(self.language)
            post.title = post_object.title
            post.description = post_object.description
            post.published_date = post_object.published_date
        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)


class DefaultBlogView(BlogView):

    def get_object(self, queryset=None):
        blog_id = settings.DEFAULT_BLOG_ID
        return get_object_or_404(Blog, pk=blog_id)


class TagView(BlogDetailView):
    template_name = "djcms_blog/tag.html"
    slug_field = "slug"
    slug_url_kwarg = "tag_slug"
    model = Tag
    object = None

    def get_context_data(self, **kwargs):
        context = super(TagView, self).get_context_data(**kwargs)
        return context

    def get(self, request, *args, **kwargs):
        self.set_language()
        self.object = self.get_object()
        lang_object = self.object.get_language_object(self.language)
        self.object.description = lang_object.description
        self.object.meta_title = lang_object.meta_title
        self.object.meta_description = lang_object.meta_description
        self.object.cover_image = self.object.cover.url if self.object.cover else settings.DEFAULT_COVER_IMAGE
        self.object.get_posts = self.object.get_posts()
        for post in self.object.get_posts:
            post_object = post.language_object(self.language)
            post.title = post_object.title
            post.description = post_object.description
            post.published_date = post_object.published_date
        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)


class AutorView(BlogDetailView):
    template_name = "djcms_blog/author.html"
    slug_field = "slug"
    slug_url_kwarg = "author_slug"
    model = Author
    object = None

    def get_context_data(self, **kwargs):
        context = super(AutorView, self).get_context_data(**kwargs)
        return context

    def get(self, request, *args, **kwargs):
        self.set_language()
        self.object = self.get_object()
        lang_object = self.object.get_language_object(self.language)
        self.object.bio = lang_object.bio
        self.object.cover_image = self.object.cover.url if self.object.cover else settings.DEFAULT_COVER_IMAGE
        self.object.get_posts = self.object.get_posts()
        for post in self.object.get_posts:
            post.title = post.language_object(self.language).title
            post.description = post.language_object(self.language).description
            post.published_date = post.language_object(self.language).published_date
        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)


class PostView(BlogDetailView):
    template_name = "djcms_blog/post.html"
    slug_field = "slug"
    slug_url_kwarg = "post_slug"
    model = Post
    object = None

    def get_context_data(self, **kwargs):
        context = super(PostView, self).get_context_data(**kwargs)
        return context

    def get(self, request, *args, **kwargs):
        self.set_language()
        self.object = self.get_object()
        if not self.object.is_published():
            raise Http404("Not found")

        lang_object = self.object.language_object(self.language)
        self.object.title_id = lang_object.id
        self.object.title = lang_object.title
        self.object.body = lang_object.body
        self.object.post_draft = lang_object.post_draft
        self.object.published = lang_object.published
        self.object.published_date = lang_object.published_date
        self.object.meta_title = lang_object.meta_title
        self.object.meta_description = lang_object.meta_description
        self.object.cover_image = self.object.cover.url if self.object.cover else settings.DEFAULT_COVER_IMAGE
        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)


class PostDraftView(PostView):
    def get_object(self, queryset=None):

        if queryset is None:
            queryset = self.get_queryset()

        slug = self.kwargs.get(self.slug_url_kwarg)

        if slug is not None:
            slug_field = self.get_slug_field()
            queryset = queryset.filter(**{slug_field: slug})

        try:
            obj = queryset.get()
        except queryset.model.DoesNotExist:
            raise Http404(
                _("No %(verbose_name)s found matching the query")
                % {"verbose_name": queryset.model._meta.verbose_name}
            )
        return obj
