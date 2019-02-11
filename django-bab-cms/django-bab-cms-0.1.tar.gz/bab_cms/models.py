from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils.text import Truncator
from django.utils.timezone import now

from mptt.models import MPTTModel, TreeForeignKey
from filebrowser.fields import FileBrowseField
from ckeditor_uploader.fields import RichTextUploadingField


class Category(models.Model):
    parent = models.ForeignKey('self', on_delete=models.CASCADE, blank=True, null=True, related_name='children')
    slug = models.SlugField(verbose_name='slug', unique=True)
    excerpt = models.CharField(max_length=128, verbose_name="résumé", blank=True)
    title = models.CharField(max_length=64)
    image = FileBrowseField("Image", max_length=200, extensions=['.jpg', '.png'], blank=True)

    prepopulated_fields = {"slug": ("title",)}

    def __str__(self):
        full_path = [self.title]

        k = self.parent
        while k is not None:
            full_path.append(k.title)
            k = k.parent
        full_path.reverse()

        return ' -> '.join(full_path[::1])

    class Meta:
        verbose_name = "Catégorie"
        verbose_name_plural = "catégories"
        unique_together = ('parent', 'slug')

    def get_absolute_url(self):
        return reverse('cms-category-detail', args=[self.slug, ])


class PublishedManager(models.Manager):
    def get_queryset(self):
        return super(PublishedManager, self).get_queryset().filter(status=Publishable.STATUS_PUBLISHED)


class Publishable(models.Model):
    STATUS_DRAFT = 0
    STATUS_PUBLISHED = 1

    STATUS = (
        (STATUS_DRAFT, 'brouillon'),
        (STATUS_PUBLISHED, 'publié'),
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="date de création"
    )
    created_by = models.ForeignKey(
        User, on_delete=models.DO_NOTHING,
        related_name='%(class)s_created_publications'
    )

    modified_at = models.DateTimeField(
        auto_now=True,
        verbose_name="date de modification",
        null=True
    )

    modified_by = models.ForeignKey(
        User,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="%(class)s_modified_publications"
    )

    published_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="date de publication"
    )

    status = models.PositiveIntegerField(
        choices=STATUS,
        default=STATUS_DRAFT,
        verbose_name='état de publication'
    )
    can_comment = models.BooleanField(
        default=False,
        verbose_name='Commentaires autorisés'
    )

    categories = models.ManyToManyField(
        Category,
        verbose_name='catégorie',
        related_name='%(class)s'
    )

    title = models.CharField(max_length=64)

    slug = models.SlugField(
        verbose_name='slug',
        unique=True
    )
    image = FileBrowseField(
        "Image",
        max_length=200,
        extensions=['.jpg', '.png'],
        blank=True
    )
    excerpt = models.CharField(
        max_length=128,
        verbose_name="résumé",
        blank=True
    )

    prepopulated_fields = {"slug": ("title",)}

    objects = models.Manager()
    published = PublishedManager()

    class Meta:
        ordering = ('-published_at',)
        abstract = True

    def __str__(self):
        return self.title

    @property
    def resume(self, num_words=10):
        if self.excerpt:
            return self.excerpt
        return Truncator(self.content).words(num_words, None, True)

    def set_status(self, status):
        """
        Set publishable Status
        :type status: Publishable.STATUS
        """
        print("set state %s" % status)
        self.status = status
        if status == self.STATUS_PUBLISHED:
            self.published_at = now()
        else:
            self.published_at = None
        self.save()


class Post(Publishable):
    content = RichTextUploadingField(blank=True)

    def get_absolute_url(self):
        return reverse('cms-post-detail', args=[self.slug, ])


class Article(MPTTModel, Publishable):
    parent = TreeForeignKey('self', blank=True, null=True, on_delete=models.CASCADE, related_name='children')
    content = RichTextUploadingField(blank=True)

    def __str__(self):
        full_path = [self.title]

        k = self.parent
        while k is not None:
            full_path.append(k.title)
            k = k.parent
        full_path.reverse()
        return ' -> '.join(full_path[::1])

    def get_absolute_url(self):
        return reverse('cms-article-detail', args=[self.slug, ])

"""
    def set_published(self, published):
        # if root node, set all descendants

        # Publishing
        if published:
            # if not root, publish only if root is published
            if self.parent and self.parent.published:
                self.published = published
                self.published_at = now()
                self.save()
                post_published_publication.send(sender=self.__class__, instance=self, created=False)

            # if root, publish only self
            if not self.parent:
                self.published = published
                self.published_at = now()
                self.save()
                post_published_publication.send(sender=self.__class__, instance=self, created=False)

        # Unpublishing
        if not published:
            # unpublish children
            for node in self.get_descendants(include_self=True).iterator():
                node.published = published
                node.published_at = None
                node.save()
                post_published_publication.send(sender=self.__class__, instance=node, created=False)
"""


class Note(models.Model):
    CSS_CLASSES = (
        ('', '-'),
        ('primary', 'primary'),
        ('secondary', 'secondary'),
        ('success', 'success'),
        ('danger', 'danger'),
        ('warning', 'warning'),
        ('info', 'info'),
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='date de création')
    content = models.TextField()
    display = models.BooleanField(default=True, verbose_name='afficher')
    css_class = models.CharField(max_length=16, choices=CSS_CLASSES, default='', verbose_name='type d\'affichage')

    def __str__(self):
        return self.content[:20]
