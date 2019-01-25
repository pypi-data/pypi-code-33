from django.conf import settings
from django.contrib import admin
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.utils.translation import gettext_lazy as _

from .models import Author, AuthorBio, Blog, BlogTitle, Post, PostTitle, Tag, TagTitle

add_string = _("Add")
view_string = _("View")


def make_published(modeladmin, request, queryset):
    for post in queryset:
        published = post.publish()
        if published:
            messages.success(request, "{} published".format(post.title))
        else:
            messages.error(request, "'{}' does not have changes".format(post.title))


make_published.short_description = "Publish selected posts"


def make_unpublished(modeladmin, request, queryset):
    for post in queryset:
        post.unpublish()


make_unpublished.short_description = "Unpublish selected posts"


class PostAdmin(admin.ModelAdmin):
    list_display = ["title", "is_published", "blog"]
    filter_horizontal = ("tags",)
    prepopulated_fields = {"slug": ("title",)}

    def is_published(self, obj):
        return obj.is_published()

    is_published.boolean = True


for lang in settings.LANGUAGES:

    def get_tag():
        lang_code = lang[0]

        def lang_tag(self, obj):
            lang_object = obj.get_language_object(lang_code)
            if lang_object:
                return '<a href="/admin/djcms_blog/posttitle/{}/" class="button">{} {}</a>'.format(
                    lang_object.id, view_string, lang_code.upper()
                )
            return '<a class="button" href="/admin/djcms_blog/posttitle/add/">{} {}</a>'.format(
                add_string, lang_code.upper()
            )

        lang_tag.short_description = lang_code.upper()
        lang_tag.allow_tags = True
        lang_tag.__name__ = lang_code
        return lang_tag

    setattr(PostAdmin, lang[0], get_tag())
    PostAdmin.list_display.append(lang[0])


class PostTitleAdmin(admin.ModelAdmin):
    change_list_template = "admin/djcms_blog/post_action.html"
    list_display = ("title", "is_edited", "post", "language", "published")
    actions = [make_published, make_unpublished]
    exclude = ("published", "published_date")

    def is_edited(self, obj):
        return obj.edited()

    is_edited.boolean = True

    def view_on_site(self, obj):
        if obj.published:
            return reverse(
                "post-detail",
                kwargs={"blog_slug": obj.post.blog.slug, "post_slug": obj.post.slug},
            )
        else:
            return reverse(
                "draft-post-detail",
                kwargs={"blog_slug": obj.post.blog.slug, "post_slug": obj.post.slug},
            )

    def get_model_perms(self, request):
        """
        Return empty perms dict thus hiding the model from admin index.
        """
        return {}

    def get_queryset(self, request):
        qs = super(PostTitleAdmin, self).get_queryset(request)
        return qs.filter(is_draft=True)


class BlogAdmin(admin.ModelAdmin):
    list_display = ["title", "slug", "post_count"]
    prepopulated_fields = {"slug": ("title",)}

    def post_count(self, obj):
        return obj.get_posts().count()

    def view_on_site(self, obj):
        return reverse("blog-main", kwargs={"blog_slug": obj.slug})


for lang in settings.LANGUAGES:

    def get_tag():
        lang_code = lang[0]

        def lang_tag(self, obj):
            lang_object = obj.get_language_object(lang_code)
            if lang_object:
                return '<a href="/admin/djcms_blog/blogtitle/{}/" class="button">{} {}</a>'.format(
                    lang_object.id, view_string, lang_code.upper()
                )
            return '<a class="button" href="/admin/djcms_blog/blogtitle/add/">{} {}</a>'.format(
                add_string, lang_code.upper()
            )

        lang_tag.short_description = lang_code.upper()
        lang_tag.allow_tags = True
        lang_tag.__name__ = lang_code
        return lang_tag

    setattr(BlogAdmin, lang[0], get_tag())
    BlogAdmin.list_display.append(lang[0])


class BlogTitleAdmin(admin.ModelAdmin):
    list_display = ("blog", "title", "language")

    def view_on_site(self, obj):
        return reverse("blog-main", kwargs={"blog_slug": obj.blog.slug})

    def get_model_perms(self, request):
        """
        Return empty perms dict thus hiding the model from admin index.
        """
        return {}


class TagAdmin(admin.ModelAdmin):
    list_display = ["name", "slug", "color", "post_count", "blog"]
    prepopulated_fields = {"slug": ("name",)}

    def post_count(self, obj):
        return obj.get_posts().count()

    def view_on_site(self, obj):
        return reverse(
            "tag-main", kwargs={"blog_slug": obj.blog.slug, "tag_slug": obj.slug}
        )


for lang in settings.LANGUAGES:

    def get_tag():
        lang_code = lang[0]

        def lang_tag(self, obj):
            lang_object = obj.get_language_object(lang_code)
            if lang_object:
                return '<a href="/admin/djcms_blog/tagtitle/{}/" class="button">{} {}</a>'.format(
                    lang_object.id, view_string, lang_code.upper()
                )
            return '<a class="button" href="/admin/djcms_blog/tagtitle/add/">{} {}</a>'.format(
                add_string, lang_code.upper()
            )

        lang_tag.short_description = lang_code.upper()
        lang_tag.allow_tags = True
        lang_tag.__name__ = lang_code
        return lang_tag

    setattr(TagAdmin, lang[0], get_tag())
    TagAdmin.list_display.append(lang[0])


class TagTitleAdmin(admin.ModelAdmin):
    list_display = ("tag", "language", "name")

    def view_on_site(self, obj):
        return reverse(
            "tag-main",
            kwargs={"blog_slug": obj.tag.blog.slug, "tag_slug": obj.tag.slug},
        )

    def get_model_perms(self, request):
        """
        Return empty perms dict thus hiding the model from admin index.
        """
        return {}


class AuthorAdmin(admin.ModelAdmin):
    list_display = ["user", "slug", "location", "website", "post_count"]

    def post_count(self, obj):
        return obj.get_posts().count()

    def view_on_site(self, obj):
        return reverse("author-main", kwargs={"author_slug": obj.slug})


for lang in settings.LANGUAGES:

    def get_tag():
        lang_code = lang[0]

        def lang_tag(self, obj):
            lang_object = obj.get_language_object(lang_code)
            if lang_object:
                return '<a href="/admin/djcms_blog/authorbio/{}/" class="button">{} {}</a>'.format(
                    lang_object.id, view_string, lang_code.upper()
                )
            return '<a class="button" href="/admin/djcms_blog/authorbio/add/">{} {}</a>'.format(
                add_string, lang_code.upper()
            )

        lang_tag.short_description = lang_code.upper()
        lang_tag.allow_tags = True
        lang_tag.__name__ = lang_code
        return lang_tag

    setattr(AuthorAdmin, lang[0], get_tag())
    AuthorAdmin.list_display.append(lang[0])


class AuthorBioAdmin(admin.ModelAdmin):
    list_display = ["author", "language"]

    def view_on_site(self, obj):
        return reverse("author-main", kwargs={"author_slug": obj.author.slug})

    def get_model_perms(self, request):
        """
        Return empty perms dict thus hiding the model from admin index.
        """
        return {}


admin.site.register(Author, AuthorAdmin)
admin.site.register(AuthorBio, AuthorBioAdmin)
admin.site.register(Blog, BlogAdmin)
admin.site.register(BlogTitle, BlogTitleAdmin)
admin.site.register(PostTitle, PostTitleAdmin)
admin.site.register(Post, PostAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(TagTitle, TagTitleAdmin)
