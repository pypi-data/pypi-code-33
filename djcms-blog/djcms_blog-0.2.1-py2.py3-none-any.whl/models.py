from django.conf import settings
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.db import models
from django.utils import timezone
from simplemde.fields import SimpleMDEField

from .settings import DEFAULT_COVER_IMAGE, DEFAULT_USER_PROFILE_IMAGE
from .utils import expire_page


def expire_blog_post(post):
    post_url = reverse(
        "post-detail",
        kwargs={"blog_slug": post.post.blog.slug, "post_slug": post.post.slug},
    )
    expire_page(post_url)
    blog_url = reverse("blog-main", kwargs={"blog_slug": post.post.blog.slug})
    expire_page(blog_url)
    author_url = reverse("author-main", kwargs={"author_slug": post.post.author.slug})
    expire_page(author_url)


class CoverImageMixin:
    cover = None

    @property
    def cover_img_url(self):
        if self.cover:
            return self.cover.url
        return DEFAULT_COVER_IMAGE


class ProfileImageMixin:
    profile_image = None

    @property
    def profile_img_url(self):
        if self.profile_image:
            return self.profile_image.url
        return DEFAULT_USER_PROFILE_IMAGE


class Author(models.Model, CoverImageMixin, ProfileImageMixin):
    user = models.OneToOneField(User, related_name="author_profile")
    cover = models.ImageField(upload_to="author_cover", blank=True, null=True)
    profile_image = models.ImageField(upload_to="image", blank=True, null=True)
    slug = models.CharField(max_length=140)
    location = models.CharField(max_length=100)
    website = models.URLField(max_length=100)
    facebook_profile = models.URLField(max_length=100)
    twitter_profile = models.URLField(max_length=100)
    block_header = SimpleMDEField(max_length=10000, blank=True, null=True)
    block_footer = SimpleMDEField(max_length=10000, blank=True, null=True)

    def __str__(self):
        return self.user.email

    def get_language_object(self, language):
        language_object = AuthorBio.objects.filter(author=self, language=language).first()
        if language_object is None:
            language_object = AuthorBio.objects.filter(author=self, language=settings.LANGUAGE_CODE).first()
        return language_object

    def has_language(self, language):
        if AuthorBio.objects.filter(author=self, language=language).first():
            return True
        return False

    def get_posts(self):
        return Post.objects.author_posts(author=self)

    def get_post_count(self):
        return Post.objects.author_posts(author=self).count()

    def get_name(self):
        return "{} {}".format(self.user.first_name, self.user.last_name)


class AuthorBio(models.Model):
    author = models.ForeignKey(Author, db_index=True)
    bio = SimpleMDEField(max_length=255)
    language = models.CharField(
        max_length=15, db_index=True, choices=settings.LANGUAGES
    )

    def __str__(self):
        return "{} {}".format(self.author, self.language)


class Blog(models.Model, CoverImageMixin):
    title = models.CharField(max_length=140)
    slug = models.CharField(max_length=140, db_index=True)
    cover = models.ImageField(upload_to="blog_cover", blank=True, null=True)
    block_header = SimpleMDEField(max_length=10000, blank=True, null=True)
    block_footer = SimpleMDEField(max_length=10000, blank=True, null=True)

    def __str__(self):
        return self.title

    def get_posts(self):
        return Post.objects.blog_posts(blog=self)

    def has_language(self, language):
        if BlogTitle.objects.filter(blog=self, language=language).first():
            return True
        return False

    def get_language_object(self, language):
        language_object = BlogTitle.objects.filter(blog=self, language=language).first()
        if language_object is None:
            language_object = BlogTitle.objects.filter(blog=self, language=settings.LANGUAGE_CODE).first()
        return language_object


class BlogTitle(models.Model):
    blog = models.ForeignKey(Blog, db_index=True)
    language = models.CharField(
        max_length=15, db_index=True, choices=settings.LANGUAGES
    )
    title = models.CharField(max_length=140)
    description = SimpleMDEField(max_length=255)
    meta_title = SimpleMDEField(max_length=70, blank=True, null=True)
    meta_description = SimpleMDEField(max_length=156, blank=True, null=True)

    class Meta:
        unique_together = ("blog", "language")

    def __str__(self):
        return self.title


class Tag(models.Model, CoverImageMixin):
    COLOR_CHOICES = (
        ("red", "red"),
        ("orange", "orange"),
        ("yellow", "yellow"),
        ("olive", "olive"),
        ("green", "green"),
        ("teal", "teal"),
        ("blue", "blue"),
        ("violet", "violet"),
        ("purple", "purple"),
        ("pink", "pink"),
        ("brown", "brown"),
        ("grey", "grey"),
        ("black", "black"),
    )
    blog = models.ForeignKey(Blog, db_index=True)
    cover = models.ImageField(upload_to="tag_cover", blank=True, null=True)
    name = models.CharField(max_length=140)
    slug = models.CharField(max_length=140)
    color = models.CharField(max_length=14, choices=COLOR_CHOICES)
    meta_title = SimpleMDEField(max_length=70, blank=True, null=True)
    meta_description = SimpleMDEField(max_length=156, blank=True, null=True)

    def __str__(self):
        return self.name

    def has_language(self, language):
        if TagTitle.objects.filter(tag=self, language=language).first():
            return True
        return False

    def get_posts(self):
        return Post.objects.published_tag(tag=self)

    def get_post_count(self):
        return Post.objects.published_tag(tag=self).count()

    def get_language_object(self, language):
        language_object = TagTitle.objects.filter(tag=self, language=language).first()
        if language_object is None:
            language_object = TagTitle.objects.filter(tag=self, language=settings.LANGUAGE_CODE).first()
        return language_object


class TagTitle(models.Model):
    tag = models.ForeignKey(Tag, db_index=True)
    language = models.CharField(
        max_length=15, db_index=True, choices=settings.LANGUAGES
    )
    name = models.CharField(max_length=140)
    description = SimpleMDEField(max_length=200)
    meta_title = SimpleMDEField(max_length=70, blank=True, null=True)
    meta_description = SimpleMDEField(max_length=156, blank=True, null=True)

    class Meta:
        unique_together = ("tag", "language")

    def __str__(self):
        return self.name


class PostManager(models.Manager):
    def published(self):
        posts = PostTitle.objects.filter(
            published=True, is_draft=False
        ).values_list("post", flat=True)
        return Post.objects.filter(id__in=posts)

    def published_tag(self, tag):
        return self.published().filter(tags__in=[tag])

    def blog_posts(self, blog):
        return self.published().filter(blog=blog)

    def author_posts(self, author):
        return self.published().filter(author=author)


class Post(models.Model, CoverImageMixin):
    blog = models.ForeignKey(Blog, db_index=True)
    title = models.CharField(max_length=255)
    slug = models.CharField(max_length=140)
    cover = models.ImageField(upload_to="post_cover", blank=True, null=True)
    author = models.ForeignKey(Author, db_index=True)
    tags = models.ManyToManyField(Tag)

    objects = PostManager()

    def __str__(self):
        return self.title

    def get_tags(self):
        return self.tags.all()

    def language_object(self, language):
        language_object = PostTitle.objects.filter(
            post=self, language=language, is_draft=False, published=True
        ).first()
        if language_object:
            return language_object
        return PostTitle.objects.filter(post=self, is_draft=False, published=True).first()

    def get_language_object(self, language):
        language_object = PostTitle.objects.filter(post=self, language=language, is_draft=True).first()
        if language_object is None:
            language_object = PostTitle.objects.filter(
                post=self, language=settings.LANGUAGE_CODE, is_draft=True).first()
        return language_object

    def has_language(self, language):
        if PostTitle.objects.filter(post=self, language=language).first():
            return True
        return False

    def is_published(self):
        if PostTitle.objects.filter(
            post=self, is_draft=False, published=True
        ).first():
            return True
        return False


class PostTitle(models.Model):
    post = models.ForeignKey(Post, db_index=True)
    title = models.CharField(max_length=255)
    language = models.CharField(
        max_length=15, db_index=True, choices=settings.LANGUAGES
    )
    description = SimpleMDEField(max_length=80000)
    body = SimpleMDEField(max_length=80000)
    meta_title = SimpleMDEField(max_length=70, blank=True, null=True)
    meta_description = SimpleMDEField(max_length=156, blank=True, null=True)
    published = models.BooleanField(blank=True, default=False)
    is_draft = models.BooleanField(
        default=True, editable=False, db_index=True
    )
    public_post_title = models.OneToOneField(
        "self",
        on_delete=models.SET_NULL,
        related_name="post_draft",
        null=True,
        editable=False,
    )
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    published_date = models.DateTimeField(blank=True, null=True)

    class Meta:
        unique_together = ("post", "language", "is_draft")

    def get_absolute_url(self):
        from django.core.urlresolvers import reverse
        return reverse('post-detail', kwargs={'blog_slug': self.post.blog.slug, 'post_slug': self.post.slug})

    def edited(self):
        if self.public_post_title:
            if all(
                (
                    self.public_post_title.post == self.post,
                    self.public_post_title.title == self.title,
                    self.public_post_title.language == self.language,
                    self.public_post_title.description == self.description,
                    self.public_post_title.body == self.body,
                    self.public_post_title.meta_title == self.meta_title,
                    self.public_post_title.meta_description == self.meta_description,
                )
            ):
                return False
            return True
        return False

    def create_public_post(self):
        publisher_public = PostTitle(
            post=self.post,
            title=self.title,
            language=self.language,
            description=self.description,
            body=self.body,
            meta_title=self.meta_title,
            meta_description=self.meta_description,
            is_draft=False,
            published=True,
            published_date=timezone.now(),
        )
        publisher_public.save()
        self.public_post_title = publisher_public
        self.published = True
        self.publisher_edited = False
        self.published_date = timezone.now()
        self.save()

    def publish(self):
        if self.public_post_title is None:
            self.create_public_post()
            expire_blog_post(self)
            return True
        else:
            if self.edited():
                publisher_public = self.public_post_title
                self.public_post_title = None
                publisher_public.delete()
                self.create_public_post()
                expire_blog_post(self)
                return True
            return False

    def unpublish(self):
        publisher_public = self.public_post_title
        self.public_post_title = None
        publisher_public.delete()
        self.published = False
        self.published_date = None
        expire_blog_post(self)
        self.save()
